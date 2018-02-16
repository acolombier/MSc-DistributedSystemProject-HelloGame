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

import Controller.ClientCLI;
import Controller.ClientInterface;
import Controller.ClientUI;
import Model.Message;
import Model.MessageBundle;
import Service.Client;
import Service.ClientImpl;
import Service.Server;

public class RunClient {
	
	private static Client client_stub;
	private static Server server;
	private static Registry registry;
	
	public static void  main(String [] args) throws RemoteException, NotBoundException {
		boolean is_using_gui = false;
		String server_addr = "127.0.0.1";
		
		for (String a: args){
			if (a.startsWith("--gui"))
				is_using_gui = true;
			else
				server_addr = a;
		}
		
		registry = LocateRegistry.getRegistry(server_addr);
		server = (Server) registry.lookup("Server");
		
		ClientInterface controler = is_using_gui ? new ClientUI() : new ClientCLI();
		
		Model.Client client;
		
		while (true) {		
			String username = controler.requestNickname();
			
			ClientImpl c = new ClientImpl(username, controler);
			client_stub = (Client) UnicastRemoteObject.exportObject(c, 0);
			
			if (server.register(client_stub)) {
				client = new Model.Client(username, c);
				break;
			}
			controler.error("Client already registered");
		}
		controler.run(server, client);
		server.unregister(client_stub.getName());
	}
}