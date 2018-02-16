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

import Controller.ClientController;
import Models.MessageBundle;
import Service.Client;
import Service.ClientImpl;
import Service.Server;
import UI.ChatServerUI;

public class RunClient {
	
	public static void  main(String [] args) throws RemoteException, NotBoundException {
		
		ClientController controller = new ClientController();
//		Scanner scanner = new Scanner(System.in);
//		String username = null;
//
//		registry = LocateRegistry.getRegistry("127.0.0.1");
//		server = (Server) registry.lookup("Server");
//		
//		while (true) {
//			System.out.println("Enter Username: ");			
//			username = scanner.nextLine();
//			ClientImpl client = new ClientImpl(username);
//			client_stub = (Client) UnicastRemoteObject.exportObject(client, 0);
//			
//			if (server.register(client_stub) ) {
//				break;
//			}
//			System.out.println("Client already registered; try again!");
//		}
//		
//		Models.Client clientModel = new Models.Client(username);
//		System.out.println("Start Chat | press q to quit");
//		String userMessage = null;
//		
//		while (! (userMessage == "q")) {
//			userMessage = scanner.nextLine();
//			System.out.println("Enter receiver name: ");
//			String receiverName = scanner.nextLine();
//			MessageBundle userMessageBundle = new MessageBundle(clientModel, userMessage, receiverName);
//			server.push(userMessageBundle);
//		}
//		server.unregister(client_stub);
	}
}
