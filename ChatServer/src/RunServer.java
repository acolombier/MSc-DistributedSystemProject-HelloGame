import java.io.File;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;
import java.util.ArrayList;

import Service.Client;
import Service.Server;
import Service.ServerImpl;

public class RunServer {
	private ArrayList<Client> connectedClients;
	
	public static void  main(String [] args) {
		try {
			File logFile = new File("message.log");
			ServerImpl server = new ServerImpl(logFile);
			
			Server server_stub = (Server) UnicastRemoteObject.exportObject(server, 8888);

			Registry registry= LocateRegistry.getRegistry();
			registry.bind("Server", server_stub);
			
			
		} catch (Exception e) {
			System.err.println("Error on server :" + e);
			e.printStackTrace();
		}
	}
}
