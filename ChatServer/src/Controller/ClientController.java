package Controller;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;

import Models.Message;
import Models.MessageBundle;
import Service.Client;
import Service.ClientImpl;
import Service.Server;
import UI.ChatServerUI;

public class ClientController implements ClientInterface 
{
	private ChatServerUI ui;
	private static Client client_stub;
	private static Server server;
	private static Registry registry;
	private static String username;
	private static Models.Client clientModel;
	
	public ClientController() {
		// TODO Auto-generated constructor stub
		this.createView();
	}
	
	private void createView() {
		ui = new ChatServerUI();
		ui.getConnectButton().addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				try {
					registry = LocateRegistry.getRegistry("127.0.0.1");
					server = (Server) registry.lookup("Server");
					
					username = ui.getUsernameField().getText();
					ClientImpl client = new ClientImpl(username);
					client_stub = (Client) UnicastRemoteObject.exportObject(client, 0);
					
					clientModel = new Models.Client(username);
					
					if (server.register(client_stub)) {
						ui.getChatFrame().setVisible(true);
						ui.getLoginFrame().dispose();
					}

				} catch (RemoteException | NotBoundException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
			}
		});

		ui.getSendButton().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				MessageBundle msgBundle = new MessageBundle(clientModel, ui.getMsgField().getText(), "bashar");
				try {
					server.push(msgBundle);
				} catch (RemoteException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				
			}
		});
		
		WindowAdapter wa = new WindowAdapter() {
			@Override
            public void windowClosing(WindowEvent we) {
            	try {
					server.unregister(username);
				} catch (RemoteException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
            }
		};
		
		ui.getChatFrame().addWindowListener(wa);

	}
	
	@Override
	public void display_message(Message m) {
		// TODO Auto-generated method stub
		this.shiftMessages();
		ui.getMsgSender()[ui.getNumOfShownMsg() - 1].setText(m.getSender().getName());
		ui.getMsg()[ui.getNumOfShownMsg() - 1].setText(m.getMessage());
	}
	
	/*
	 * to add new message to the list we need to shift the latest 9 messages
	 */
	private void shiftMessages()
	{
		for(int i=0; i < ui.getNumOfShownMsg() - 1; i++) {
			ui.getMsgSender()[i].setText(ui.getMsgSender()[i+i].getText());
			ui.getMsg()[i].setText(ui.getMsg()[i+i].getText());
		}
	}


}
