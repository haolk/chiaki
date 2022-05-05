// SPDX-License-Identifier: LicenseRef-AGPL-3.0-only-OpenSSL

#include <streamwindow.h>
#include <streamsession.h>
#include <avopenglwidget.h>
#include <loginpindialog.h>
#include <settings.h>

#include <QLabel>
#include <QMessageBox>
#include <QCoreApplication>
#include <QAction>
#include <mainwindow.h>
#include <QApplication>
#include "avopenglframeuploader.h"
#include <sys/errno.h>

FrameListener::FrameListener(StreamSession *s)
{
    //
	// Initialize ZMQ context and socket
	// TODO: Use POLL instead of PAIR
	//
    z_context = zmq_ctx_new();    
    z_socket = zmq_socket(z_context, ZMQ_REP);    
    session = s;
    stop = false;
}

void FrameListener::run()
{

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
		int rc;
		rc = zmq_bind(z_socket, mainWnd->getSettings()->GetFrameZMQAddr().toStdString().c_str());
		assert(rc==0);
		while (!stop)
		{
			zmq_msg_t msg;
			rc = zmq_msg_init(&msg);
			assert(rc==0);
			rc = zmq_msg_recv(&msg, z_socket, 0);
			if (rc != -1)
			{
				cv::Mat &image = images_rb[images_rb_ptr];
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
	}
}

void FrameListener::terminate()
{
    zmq_close(z_socket);
    zmq_ctx_destroy(z_context);
    stop = true;
}

JSEventListener::JSEventListener(StreamSession *s)
{
    //
	// Initialize ZMQ context and socket
	// TODO: Use POLL instead of PAIR
	//
    z_context = zmq_ctx_new();    
    z_socket = zmq_socket(z_context, ZMQ_PULL);    
    session = s;
    stop = false;
}

void JSEventListener::run()
{

	MainWindow *mainWnd = NULL;
    int idx = 0;
    while (idx < qApp->topLevelWidgets().length() && mainWnd == NULL)
    {
        mainWnd = dynamic_cast<MainWindow*>(qApp->topLevelWidgets()[idx]);
        idx++;
    }
    assert(mainWnd);
    
    if (mainWnd->getSettings()->GetCmdZMQState())
    {
		int rc;
		rc = zmq_bind(z_socket, mainWnd->getSettings()->GetCmdZMQAddr().toStdString().c_str());
		assert(rc==0);
		while (!stop)
		{
			zmq_msg_t msg;
			rc = zmq_msg_init(&msg);
			assert(rc==0);
			rc = zmq_msg_recv(&msg, z_socket, 0);
			if (rc != -1)
			{
				JSEvent_Struct event;
				memcpy(&event, zmq_msg_data(&msg), zmq_msg_size(&msg));

				session->SendJSEvent(event);
			}
		}
	}
}

void JSEventListener::terminate()
{
    zmq_close(z_socket);
    zmq_ctx_destroy(z_context);
    stop = true;
}


StreamWindow::StreamWindow(const StreamSessionConnectInfo &connect_info, QWidget *parent)
	: QMainWindow(parent),
	connect_info(connect_info)
{
	setAttribute(Qt::WA_DeleteOnClose);
	setWindowTitle(qApp->applicationName() + " | Stream");
		
	session = nullptr;
	av_widget = nullptr;

	try
	{
		if(connect_info.fullscreen)
			showFullScreen();
		Init();
	}
	catch(const Exception &e)
	{
		QMessageBox::critical(this, tr("Stream failed"), tr("Failed to initialize Stream Session: %1").arg(e.what()));
		close();
	}
}

StreamWindow::~StreamWindow()
{
	// make sure av_widget is always deleted before the session
    if (jsEventListener) // Make sure thread is terminated
    {
        jsEventListener->terminate();
        delete jsEventListener;
    } 
	if (frameListener)
	{
		frameListener->terminate();
		delete frameListener;
	}
	delete av_widget;
}

void StreamWindow::Init()
{
	session = new StreamSession(connect_info, this);

	connect(session, &StreamSession::SessionQuit, this, &StreamWindow::SessionQuit);
	connect(session, &StreamSession::LoginPINRequested, this, &StreamWindow::LoginPINRequested);

	if(session->GetFfmpegDecoder())
	{
		av_widget = new AVOpenGLWidget(session, this);
		setCentralWidget(av_widget);
	}
	else
	{
		QWidget *bg_widget = new QWidget(this);
		bg_widget->setStyleSheet("background-color: black;");
		setCentralWidget(bg_widget);
	}

	grabKeyboard();

	session->Start();

	auto fullscreen_action = new QAction(tr("Fullscreen"), this);
	fullscreen_action->setShortcut(Qt::Key_F11);
	addAction(fullscreen_action);
	connect(fullscreen_action, &QAction::triggered, this, &StreamWindow::ToggleFullscreen);

	resize(connect_info.video_profile.width, connect_info.video_profile.height);
    
    jsEventListener = new JSEventListener(session);
    jsEventListener->start();

	frameListener = new FrameListener(session);
	frameListener->start();
    
	show();
}

void StreamWindow::keyPressEvent(QKeyEvent *event)
{
	if(session)
		session->HandleKeyboardEvent(event);
}

void StreamWindow::keyReleaseEvent(QKeyEvent *event)
{
	if(session)
		session->HandleKeyboardEvent(event);
}

void StreamWindow::mousePressEvent(QMouseEvent *event)
{
	if(session)
		session->HandleMouseEvent(event);
}

void StreamWindow::mouseReleaseEvent(QMouseEvent *event)
{
	if(session)
		session->HandleMouseEvent(event);
}

void StreamWindow::mouseDoubleClickEvent(QMouseEvent *event)
{
	ToggleFullscreen();

	QMainWindow::mouseDoubleClickEvent(event);
}

void StreamWindow::closeEvent(QCloseEvent *event)
{
	if (jsEventListener) {
		jsEventListener->terminate();
		delete jsEventListener;
		jsEventListener = NULL;
	}

	if(session)
	{
		if(session->IsConnected())
		{
			bool sleep = false;
			switch(connect_info.settings->GetDisconnectAction())
			{
				case DisconnectAction::Ask: {
					auto res = QMessageBox::question(this, tr("Disconnect Session"), tr("Do you want the Console to go into sleep mode?"),
							QMessageBox::Yes | QMessageBox::No | QMessageBox::Cancel);
					switch(res)
					{
						case QMessageBox::Yes:
							sleep = true;
							break;
						case QMessageBox::Cancel:
							event->ignore();
							return;
						default:
							break;
					}
					break;
				}
				case DisconnectAction::AlwaysSleep:
					sleep = true;
					break;
				default:
					break;
			}
			if(sleep)
				session->GoToBed();
		}
		session->Stop();
	}
}

void StreamWindow::SessionQuit(ChiakiQuitReason reason, const QString &reason_str)
{
	if(reason != CHIAKI_QUIT_REASON_STOPPED)
	{
		QString m = tr("Chiaki Session has quit") + ":\n" + chiaki_quit_reason_string(reason);
		if(!reason_str.isEmpty())
			m += "\n" + tr("Reason") + ": \"" + reason_str + "\"";
		QMessageBox::critical(this, tr("Session has quit"), m);
	}
	close();
}

void StreamWindow::LoginPINRequested(bool incorrect)
{
	auto dialog = new LoginPINDialog(incorrect, this);
	dialog->setAttribute(Qt::WA_DeleteOnClose);
	connect(dialog, &QDialog::finished, this, [this, dialog](int result) {
		grabKeyboard();

		if(!session)
			return;

		if(result == QDialog::Accepted)
			session->SetLoginPIN(dialog->GetPIN());
		else
			session->Stop();
	});
	releaseKeyboard();
	dialog->show();
}

void StreamWindow::ToggleFullscreen()
{
	if(isFullScreen())
		showNormal();
	else
	{
		showFullScreen();
		if(av_widget)
			av_widget->HideMouse();
	}
}

void StreamWindow::resizeEvent(QResizeEvent *event)
{
	UpdateVideoTransform();
	QMainWindow::resizeEvent(event);
}

void StreamWindow::moveEvent(QMoveEvent *event)
{
	UpdateVideoTransform();
	QMainWindow::moveEvent(event);
}

void StreamWindow::changeEvent(QEvent *event)
{
	if(event->type() == QEvent::ActivationChange)
		UpdateVideoTransform();
	QMainWindow::changeEvent(event);
}

void StreamWindow::UpdateVideoTransform()
{
#if CHIAKI_LIB_ENABLE_PI_DECODER
	ChiakiPiDecoder *pi_decoder = session->GetPiDecoder();
	if(pi_decoder)
	{
		QRect r = geometry();
		chiaki_pi_decoder_set_params(pi_decoder, r.x(), r.y(), r.width(), r.height(), isActiveWindow());
	}
#endif
}
