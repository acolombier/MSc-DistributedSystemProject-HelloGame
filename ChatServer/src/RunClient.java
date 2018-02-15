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
import java.util.Scanner;

import javax.swing.JFrame;
import javax.swing.JLabel;

import Models.MessageBundle;
import Service.Client;
import Service.ClientImpl;
import Service.Server;
import UI.ChatServerUI;

public class RunClient {
	
	private static Client client_stub;
	private static Server server;
	private static Registry registry;
	
	public static void  main(String [] args) throws RemoteException, NotBoundException {
		
		Scanner scanner = new Scanner(System.in);
		String username = null;

		registry = LocateRegistry.getRegistry("127.0.0.1");
		server = (Server) registry.lookup("Server");
		
		while (true) {
			System.out.println("Enter Username: ");			
			username = scanner.nextLine();
			ClientImpl client = new ClientImpl(username);
			client_stub = (Client) UnicastRemoteObject.exportObject(client, 0);
			
			if (server.register(client_stub) ) {
				break;
			}
			System.out.println("Client already registered; try again!");
		}
		
		Models.Client clientModel = new Models.Client(username);
		System.out.println("Start Chat | press q to quit");
		String userMessage = null;
		
		while (! (userMessage == "q")) {
			userMessage = scanner.nextLine();
			System.out.println("Enter receiver name: ");
			String receiverName = scanner.nextLine();
			MessageBundle userMessageBundle = new MessageBundle(clientModel, userMessage, receiverName);
			server.push(userMessageBundle);
		}
		server.unregister(client_stub);
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
			
			TextField textField = new TextField(10);
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
						server.unregister(client_stub);
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
