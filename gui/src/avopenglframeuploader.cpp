// SPDX-License-Identifier: LicenseRef-AGPL-3.0-only-OpenSSL

#include <avopenglframeuploader.h>
#include <avopenglwidget.h>
#include <streamsession.h>

#include <QOpenGLContext>
#include <QOpenGLFunctions>

#include <mainwindow.h>
#include <settings.h>
#include <QApplication>

#define IMAGES_RB_SIZE (120)
cv::Mat images_rb[IMAGES_RB_SIZE];
volatile unsigned int images_rb_ptr = 0;

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
        images_rb_ptr = 0;
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
 

    int ptr = (images_rb_ptr+1) % IMAGES_RB_SIZE;
    if (images_rb[ptr].rows != height || images_rb[ptr].cols != width || images_rb[ptr].type() != CV_8UC3) {
        images_rb[ptr] = cv::Mat(height, width, CV_8UC3);
    }

    int cvLinesizes[1];
    cvLinesizes[0] = images_rb[ptr].step1();
 
    // Convert the colour format and write directly to the opencv matrix
    // Note here we use RGB24
    SwsContext* conversion = sws_getContext(width, height, (AVPixelFormat) frame->format, width, height, AV_PIX_FMT_RGB24, SWS_FAST_BILINEAR, NULL, NULL, NULL);
    sws_scale(conversion, frame->data, frame->linesize, 0, height, &images_rb[ptr].data, cvLinesizes);
    sws_freeContext(conversion);

    images_rb_ptr = ptr;

    cv::Mat &image = images_rb[ptr];
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
        
    SendFrame(next_frame); // Send frame to ZMQ Server	av_frame_free(&next_frame);

    av_frame_free(&next_frame);
	if(success)
		widget->SwapFrames();
}
