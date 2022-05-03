// SPDX-License-Identifier: LicenseRef-AGPL-3.0-only-OpenSSL

#ifndef CHIAKI_GUI_STREAMWINDOW_H
#define CHIAKI_GUI_STREAMWINDOW_H

#include <QMainWindow>

#include "streamsession.h"


class QLabel;
class AVOpenGLWidget;


#include <QThread>
#include <zmq.h>
#include <chrono>
#include <thread>

class JSEventListener: public QThread
{
    public:
        JSEventListener(StreamSession *s);
        void run();
        void terminate();
        
    private:
        void *z_context;
        void *z_socket;
        StreamSession *session;
        bool stop;
};

class StreamWindow: public QMainWindow
{
	Q_OBJECT

	public:
		explicit StreamWindow(const StreamSessionConnectInfo &connect_info, QWidget *parent = nullptr);
		~StreamWindow() override;

	private:
		const StreamSessionConnectInfo connect_info;
		StreamSession *session;

		AVOpenGLWidget *av_widget;

		void Init();
		void UpdateVideoTransform();

		JSEventListener *jsEventListener;

	protected:
		void keyPressEvent(QKeyEvent *event) override;
		void keyReleaseEvent(QKeyEvent *event) override;
		void closeEvent(QCloseEvent *event) override;
		void mousePressEvent(QMouseEvent *event) override;
		void mouseReleaseEvent(QMouseEvent *event) override;
		void mouseDoubleClickEvent(QMouseEvent *event) override;
		void resizeEvent(QResizeEvent *event) override;
		void moveEvent(QMoveEvent *event) override;
		void changeEvent(QEvent *event) override;

	private slots:
		void SessionQuit(ChiakiQuitReason reason, const QString &reason_str);
		void LoginPINRequested(bool incorrect);
		void ToggleFullscreen();
};

#endif // CHIAKI_GUI_STREAMWINDOW_H
