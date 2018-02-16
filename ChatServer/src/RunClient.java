import java.awt.Button;
import java.awt.CardLayout;
import java.awt.FlowLayout;
import java.awt.Label;
import java.awt.TextField;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;
import java.util.Date;
import java.util.Scanner;

import javax.swing.JFrame;
import javax.swing.JLabel;

import Controller.ClientInterface;
import Models.Message;
import Models.MessageBundle;
import Service.Client;
import Service.ClientImpl;
import Service.Server;

public class RunClient {
	
	private static Client client_stub;
	private static Server server;
	private static Registry registry;
	
	public static void  main(String [] args) throws RemoteException, NotBoundException {
		
		Scanner scanner = new Scanner(System.in);
		
		registry = LocateRegistry.getRegistry("127.0.0.1");
		server = (Server) registry.lookup("Server");
		ClientImpl client;
		
		Models.Client clientModel;
		
		while (true) {
			System.out.println("Enter Username: ");			
			final String username = scanner.nextLine();
			client = new ClientImpl(username);
			client.setInterface(new ClientInterface(){
				@Override
				public void display_message(Message m) {
					Date date = new Date(m.getTime());
					if (m.getSender() == null)
						System.out.println("[+"+date.toString()+"] ***"+m.getMessage()+"***");	
					else if (m.getReceiver() != null)
						System.out.println("[+"+date.toString()+"][Private] *"+m.getSender().toString()+"*: "+m.getMessage());	
					else
						System.out.println(m.toString());					
				}
				
			});
			client_stub = (Client) UnicastRemoteObject.exportObject(client, 0);
			
			if (server.register(client_stub) ) {
				clientModel = new Models.Client(username);
				break;
			}
			System.out.println("Client already registered; try again!");
		}

		System.out.println("Start Chat | Type '/help' to get some help");
		
		while (true) {
			String message = scanner.nextLine();
			if (message.equals("/quit"))
				break;
			
			MessageBundle userMessageBundle;
			
			if (message.startsWith("@"))
				userMessageBundle = new MessageBundle(clientModel, message.split(" ", 2)[1], message.split(" ")[0].substring(1));
			else				
				userMessageBundle = new MessageBundle(clientModel, message);
			server.push(userMessageBundle);
		}
		server.unregister(client_stub.getName());
	}
	
	RunClient() {
		new window1().setVisible(true);
	}

	class window1 extends JFrame {
		public window1() {
			this.initialize();
			this.setVisible(true);
		}
		
		private void initialize() {
//			frame = new JFrame();
			this.setBounds(100, 100, 450, 300);
			this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

			JLabel lblNewLabel_1 = new JLabel("Connect To Chat Server");
			this.add(lblNewLabel_1);
			
			Button button = new Button("Connect");
			this.add(button);
			
			JLabel lblNewLabel = new JLabel("User Name");
			this.add(lblNewLabel);
			
			final TextField textField = new TextField(10);
			textField.setSize(10, 20);
			this.add(textField);
			
			
			this.getContentPane().setLayout(new FlowLayout());
//			frame.setSize(300, 300);
			
			
			button.addActionListener(new ActionListener() {
				
				@Override
				public void actionPerformed(ActionEvent e) {
					// TODO Auto-generated method stub
					try {
						registry = LocateRegistry.getRegistry("127.0.0.1");
						server = (Server) registry.lookup("Server");
						
						
						ClientImpl client = new ClientImpl(textField.getText());
						client_stub = (Client) UnicastRemoteObject.exportObject(client, 0);
						
//						boolean x = server.register(client_stub);
//						System.out.println(x);
						
						if (server.register(client_stub)) {
							new window2().setVisible(true);
							
						}

					} catch (RemoteException | NotBoundException e1) {
						// TODO Auto-generated catch block
						e1.printStackTrace();
					}
				}
			});
			
			this.addWindowListener( new WindowAdapter() {
	            @Override
	            public void windowClosing(WindowEvent we) {
	            	try {
						server.unregister(client_stub.getName());
					} catch (RemoteException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
	            }
	        } );
		}
	}
	
	class window2 extends JFrame {
		window2() {
			this.initialize();
			this.setVisible(false);
		}
		
		private void initialize() {
//			frame = new JFrame();
			this.setBounds(100, 100, 450, 300);
			this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
			
			this.add(new JLabel());
			this.add(new JLabel());
			this.add(new JLabel());
			this.add(new JLabel());
			this.add(new JLabel());
			this.add(new JLabel());
			
		}
	}

}
