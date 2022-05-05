// SPDX-License-Identifier: LicenseRef-AGPL-3.0-only-OpenSSL

#ifndef CHIAKI_AVOPENGLFRAMEUPLOADER_H
#define CHIAKI_AVOPENGLFRAMEUPLOADER_H

#include <QObject>
#include <QOpenGLWidget>

#include <chiaki/ffmpegdecoder.h>

#include <zmq.h>
extern "C"
{
	#include <libavcodec/avcodec.h>
}
extern "C"
{
	#include "libswscale/swscale.h"
}

#include <opencv2/core/core.hpp>

class StreamSession;
class AVOpenGLWidget;
class QSurface;

class AVOpenGLFrameUploader: public QObject
{
	Q_OBJECT

	private:
		StreamSession *session;
		AVOpenGLWidget *widget;
		QOpenGLContext *context;
		QSurface *surface;

	private:
		void *z_context;
		void *z_socket;
		void SendFrame(AVFrame *frame);

	private slots:
		void UpdateFrameFromDecoder();

	public:
		AVOpenGLFrameUploader(StreamSession *session, AVOpenGLWidget *widget, QOpenGLContext *context, QSurface *surface);
		~AVOpenGLFrameUploader();
};

extern cv::Mat images_rb[120];
extern volatile unsigned int images_rb_ptr;

#endif // CHIAKI_AVOPENGLFRAMEUPLOADER_H
