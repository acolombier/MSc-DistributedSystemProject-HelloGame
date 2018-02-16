import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;

import Controller.ClientCLI;
import Controller.ClientInterface;
import Controller.ClientUI;
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
		
		Model.Client client = null;
		ClientImpl c;
		
		while (true) {		
			String username = controler.requestNickname();
			
			c = new ClientImpl(username, controler);
			client_stub = (Client) UnicastRemoteObject.exportObject(c, 0);
			
			if (server.register(client_stub)) {
				client = new Model.Client(username, c);
				break;
			}
			controler.error("Client already registered");
		}
		
		controler.run(server, client);
		server.unregister(client_stub.getName());
		UnicastRemoteObject.unexportObject(c, false);
	}
}