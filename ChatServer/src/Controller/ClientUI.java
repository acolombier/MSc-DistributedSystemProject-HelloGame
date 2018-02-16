package Controller;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.nio.channels.ShutdownChannelGroupException;
import java.rmi.RemoteException;

import javax.swing.JFrame;
import javax.swing.JOptionPane;

import Model.Client;
import Model.Message;
import Model.MessageBundle;
import Service.Server;
import UI.ChatServerUI;

public class ClientUI implements ClientInterface {
	
	private ChatServerUI ui;
	private String userName;
	private String message;
	
	public ClientUI() {
		ui = new ChatServerUI();
		userName = JOptionPane.showInputDialog(
	        ui.getLoginFrame(), 
	        "Enter Username",
	        JOptionPane.QUESTION_MESSAGE 
	    );
		ui = new ChatServerUI();
	}
	
	@Override
	public void display_message(Message m) {
		// TODO Auto-generated method stub
//		this.shiftMessages();
//		ui.getMsgSender()[ui.getNumOfShownMsg() - 1].setText(m.getSender().getName());
//		ui.getMsg()[ui.getNumOfShownMsg() - 1].setText(m.getMessage());
	}
	
	/*
	 * to add new message to the list we need to shift the latest 9 messages
	 */
	private void shiftMessages()
	{
//		for(int i=0; i < ui.getNumOfShownMsg() - 1; i++) {
//			ui.getMsgSender()[i].setText(ui.getMsgSender()[i+i].getText());
//			ui.getMsg()[i].setText(ui.getMsg()[i+i].getText());
//		}
	}

	@Override
	public void run(final Server server, final Client client) throws RemoteException {
		// TODO Auto-generated method stub
		ui.getChatFrame().setVisible(true);
		ui.getSendButton().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				message = ui.getMsgField().getText();
				
				MessageBundle userMessageBundle;
				if (message.startsWith("@"))
					userMessageBundle = new MessageBundle(client, message.split(" ", 2)[1], message.split(" ")[0].substring(1));
				else				
					userMessageBundle = new MessageBundle(client, message);
				
				try {
					server.push(userMessageBundle);
				} catch (RemoteException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
			}
		});
		
		WindowAdapter wa = new WindowAdapter() {
			@Override
            public void windowClosing(WindowEvent we) {
//				message = "/quit";
            }
		};	
		ui.getChatFrame().addWindowListener(wa);
		
		while(!message.equals("/quit"));
	}

	@Override
	public String requestNickname() {
		// TODO Auto-generated method stub
		return userName;
	}

	@Override
	public void error(String s) {
		JOptionPane.showInputDialog(
	        ui.getLoginFrame(), 
	        s,
	        JOptionPane.ERROR_MESSAGE
	    );
		
	}
}
