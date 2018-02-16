import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;
import java.util.ArrayList;
import java.util.Map.Entry;
import java.util.Scanner;

import Model.Message;
import Service.Client;
import Service.Server;
import Service.ServerImpl;
import Service.ServerImpl.Command;

public class RunServer {
	private ArrayList<Client> connectedClients;
	
	public static void  main(String [] args) {
		try {
			File logFile = new File("message.log");
			if (!logFile.exists()){
				ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(logFile));
				oos.flush();
				oos.close();
			}
			ServerImpl server = new ServerImpl(logFile);
			
			Server server_stub = (Server) UnicastRemoteObject.exportObject(server, 8888);

			Registry registry = LocateRegistry.getRegistry();
			registry.bind("Server", server_stub);

			Scanner scanner = new Scanner(System.in);
			
			boolean server_runing = true;
			
			while (server_runing) {
				String[] payload = scanner.nextLine().substring(1).split(" ", 2);
				String body = "";
				
				switch (ServerImpl.Command.valueOf(payload[0].toUpperCase())){
				case HELP:
					for (ServerImpl.Command c: ServerImpl.Command.values())
						body += "/"+c.name().toLowerCase()+c.getArgs()+"\t"+c.getDescription()+"\n";
					break;
				case LIST:
					body = Integer.valueOf(server.getClients().size())+" connected client(s): \n";
					for (String nickname: server.getClients().keySet())
						body += nickname+"\n";
					break;
				case HISTORY:
					if (payload.length == 2){
						int c = 0, n = Integer.valueOf(payload[1]);
						n = n > 0  && n <= server.getMessages().size() ? n : server.getMessages().size();
		
						for (int i = server.getMessages().size() - 1; i >= 0 && n > 0; i--){
							body = "\t"+server.getMessages().get(i).toString()+"\n" + body;
							n--; c++;
						}
					
						body += " "+Integer.valueOf(c)+" messages displayed";
					} else
						body = "\nUsage: /history <nb message>\n";
					break;
				case QUIT:
					server_runing = false;
					for (Entry<String, Model.Client> e: server.getClients().entrySet())
						e.getValue().getInterface().send(Message.buildSystemMessage("Server is exiting", Message.Type.DISCONNECT));
					System.out.println("Stopping the server...");
					break;
				default:
					break;			
				}
				System.out.println(body);
			}
			registry.unbind("Server");
			UnicastRemoteObject.unexportObject(server, false);
			
		} catch (Exception e) {
			System.err.println("Error on server :" + e);
			e.printStackTrace();
		}
	}
}
