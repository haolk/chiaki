// SPDX-License-Identifier: LicenseRef-AGPL-3.0-only-OpenSSL

#include <avopenglframeuploader.h>
#include <avopenglwidget.h>
#include <streamsession.h>

#include <QOpenGLContext>
#include <QOpenGLFunctions>

#include <mainwindow.h>
#include <settings.h>
#include <QApplication>


AVOpenGLFrameUploader::AVOpenGLFrameUploader(StreamSession *session, AVOpenGLWidget *widget, QOpenGLContext *context, QSurface *surface)
	: QObject(nullptr),
	session(session),
	widget(widget),
	context(context),
	surface(surface)
{
	connect(session, &StreamSession::FfmpegFrameAvailable, this, &AVOpenGLFrameUploader::UpdateFrameFromDecoder);
	z_context = NULL;
	MainWindow *mainWnd = NULL;
    int idx = 0;
    while (idx < qApp->topLevelWidgets().length() && mainWnd == NULL)
    {
        mainWnd = dynamic_cast<MainWindow*>(qApp->topLevelWidgets()[idx]);
        idx++;
    }
    assert(mainWnd);
    
    if (mainWnd->getSettings()->GetFrameZMQState())
    {
        z_context = zmq_ctx_new();    
        z_socket = zmq_socket(z_context, ZMQ_PUSH);
        int on = 1;
        zmq_setsockopt(z_socket, ZMQ_IMMEDIATE, &on, sizeof(on));
        zmq_bind(z_socket, mainWnd->getSettings()->GetFrameZMQAddr().toStdString().c_str());
    }     
}

AVOpenGLFrameUploader::~AVOpenGLFrameUploader()
{
    // Destory zmq
    if (z_context)
    {
        zmq_close(z_socket);
        zmq_ctx_destroy(z_context);
        z_context = z_socket = NULL;
    }
}

void AVOpenGLFrameUploader::SendFrame(AVFrame *frame)
{
    //
    // FFMPEG AVFrame to OpenCV Mat conversion
    // based on https://timvanoosterhout.wordpress.com/2015/07/02/converting-an-ffmpeg-avframe-to-and-opencv-mat/
    //
    
    int width = frame->width;
    int height = frame->height;
 
    // Allocate the opencv mat and store its stride in a 1-element array
    cv::Mat image;
    if (image.rows != height || image.cols != width || image.type() != CV_8UC3) image = cv::Mat(height, width, CV_8UC3);
    int cvLinesizes[1];
    cvLinesizes[0] = image.step1();
 
    // Convert the colour format and write directly to the opencv matrix
    // Note here we use RGB24
    SwsContext* conversion = sws_getContext(width, height, (AVPixelFormat) frame->format, width, height, AV_PIX_FMT_RGB24, SWS_FAST_BILINEAR, NULL, NULL, NULL);
    sws_scale(conversion, frame->data, frame->linesize, 0, height, &image.data, cvLinesizes);
    sws_freeContext(conversion);
   
    
    //
    // Pack up image data with height, width and channels information
    // and send to Python server using ZMQ.
    //
    {
        assert(sizeof(unsigned short) == 2); // Make sure unsigned short length is 2
        int buf_len = sizeof(unsigned short) * 3 + image.total() * image.elemSize();
        unsigned char *buf = new unsigned char[buf_len];
        unsigned short height = image.size().height;
        unsigned short width = image.size().width;
        unsigned short channels = image.channels();
        memcpy(buf, &height, sizeof(unsigned short));
        memcpy(buf + sizeof(unsigned short), &width, sizeof(unsigned short));
        memcpy(buf + sizeof(unsigned short) * 2, &channels, sizeof(unsigned short));
        memcpy(buf + sizeof(unsigned short) * 3, image.data, image.total() * image.elemSize());

        zmq_msg_t msg;
        int rc = zmq_msg_init_size(&msg, buf_len);
        assert(rc==0);
        memcpy(zmq_msg_data(&msg), buf, buf_len);
        rc = zmq_msg_send(&msg, z_socket, ZMQ_DONTWAIT);

        delete[] buf;
    }
}

void AVOpenGLFrameUploader::UpdateFrameFromDecoder()
{
	ChiakiFfmpegDecoder *decoder = session->GetFfmpegDecoder();
	if(!decoder)
	{
		CHIAKI_LOGE(session->GetChiakiLog(), "Session has no ffmpeg decoder");
		return;
	}

	if(QOpenGLContext::currentContext() != context)
		context->makeCurrent(surface);

	AVFrame *next_frame = chiaki_ffmpeg_decoder_pull_frame(decoder);
	if(!next_frame)
		return;

    bool server_mode = false; // Chiaki server mode - no display in main window
    bool success = false;
    if (!server_mode)
        success = widget->GetBackgroundFrame()->Update(next_frame, decoder->log);
        
    if (z_context)
        SendFrame(next_frame); // Send frame to ZMQ Server	av_frame_free(&next_frame);

	if(success)
		widget->SwapFrames();
}
