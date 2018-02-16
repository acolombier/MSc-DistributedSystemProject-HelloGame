package Controller;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.nio.channels.ShutdownChannelGroupException;
import java.rmi.RemoteException;
import java.util.Date;

import javax.swing.JFrame;
import javax.swing.JOptionPane;

import java.util.concurrent.locks.Condition;

import Model.Client;
import Model.Message;
import Model.MessageBundle;
import Service.Server;
import UI.ChatAppUI;

public class ClientUI implements ClientInterface, ActionListener {
	
	private ChatAppUI ui;
	private String message;
	
	private Object runObject;
	private Client mClient;
	private Server mServer;
	
	public ClientUI() {
		ui = new ChatAppUI();
		
		runObject = new Object();
		
		ui.getMainFrame().addWindowListener(new WindowListener(){
			@Override
			public void windowActivated(WindowEvent arg0) {}

			@Override
			public void windowClosed(WindowEvent arg0) {}

			@Override
			public void windowClosing(WindowEvent arg0) {
				synchronized(runObject){
					runObject.notify();
				}
			}

			@Override
			public void windowDeactivated(WindowEvent arg0) {}

			@Override
			public void windowDeiconified(WindowEvent arg0) {}

			@Override
			public void windowIconified(WindowEvent arg0) {}

			@Override
			public void windowOpened(WindowEvent arg0) {}
			
		});
	}
	
	@Override
	public void display_message(Message m) {
		Date date = new Date(m.getTime());
		String format;
		if (m.getSender() == null){
			format = "["+date.toString()+"] ***"+m.getMessage()+"***";

			if (m.getType() == Message.Type.DISCONNECT){
				ui.getSendButton().setEnabled(false);
				ui.getMessageField().setEnabled(false);
			}
		}
		else
			format = m.toString();	
		ui.getChatBox().setText(ui.getChatBox().getText()+format+"\n");
		ui.getChatBox().invalidate();
		ui.scrollDown();
	}

	@Override
	public void run(Server server, Client client) throws RemoteException {
		ui.getMainFrame().show();
		
		ui.getChatBox().setEnabled(true);
		ui.getSendButton().setEnabled(true);
		ui.getMessageField().setEnabled(true);

		mServer = server;
		mClient = client;
		
		ui.getSendButton().addActionListener(this);
		ui.getMessageField().addKeyListener(new KeyAdapter() {
	        @Override
	        public void keyPressed(KeyEvent e) {
	            if(e.getKeyCode() == KeyEvent.VK_ENTER){
	            	actionPerformed(null);
	            }
	        }

	    });
		
		ui.getMessageField().requestFocus();
		
		synchronized(runObject) {
			try {
				runObject.wait();
			} catch (InterruptedException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
		}
	}

	@Override
	public String requestNickname() {
		return JOptionPane.showInputDialog(ui.getMainFrame(), "What's your nickname?");
	}

	@Override
	public void error(String s) {
		JOptionPane.showMessageDialog(ui.getMainFrame(), s, "Error", JOptionPane.ERROR_MESSAGE);		
	}

	@Override
	public void actionPerformed(ActionEvent e) {
		message = ui.getMessageField().getText();
		ui.getMessageField().setText("");
		ui.getMessageField().requestFocus();
		
		MessageBundle userMessageBundle;

		if (message.equals("/quit"))
			ui.getMainFrame().dispatchEvent(new WindowEvent(ui.getMainFrame(), WindowEvent.WINDOW_CLOSING));
			
		if (message.startsWith("@")){
			String[] payload = message.split(" ", 2);
			if (payload.length != 2){
				JOptionPane.showMessageDialog(ui.getMainFrame(), "Please type a message", "Error", JOptionPane.ERROR_MESSAGE);
				return;
			}
			userMessageBundle = new MessageBundle(mClient, payload[1], payload[0].substring(1));
		}
		else				
			userMessageBundle = new MessageBundle(mClient, message);
		
		try {
			mServer.push(userMessageBundle);
		} catch (RemoteException e1) {
			JOptionPane.showMessageDialog(ui.getMainFrame(), "An error has occured. Please check the log for more info.", "Error", JOptionPane.ERROR_MESSAGE);
			e1.printStackTrace();
		}		
	}
}
