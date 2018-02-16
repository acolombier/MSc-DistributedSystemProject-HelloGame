package Controller;

import java.rmi.RemoteException;
import java.util.Date;
import java.util.Scanner;

import Model.Message;
import Model.MessageBundle;
import Service.Server;

public class ClientCLI implements ClientInterface {

	@Override
	public void display_message(Message m) {
		Date date = new Date(m.getTime());
		if (m.getSender() == null){
			System.out.println("[+"+date.toString()+"] ***"+m.getMessage()+"***");
//			
//			if (m.getType() == Message.Type.DISCONNECT)
//				
		}
		else if (m.getReceiver() != null)
			System.out.println("[+"+date.toString()+"][Private] *"+m.getSender().toString()+"*: "+m.getMessage());	
		else
			System.out.println(m.toString());		
	}

	@Override
	public void run(Server server, Model.Client client) throws RemoteException {
		Scanner scanner = new Scanner(System.in);


		System.out.println("Start Chat | Type '/help' to get some help");
		
		while (true) {
			String message = scanner.nextLine();
			if (message.equals("/quit"))
				break;
			
			MessageBundle userMessageBundle;
			
			if (message.startsWith("@"))
				userMessageBundle = new MessageBundle(client, message.split(" ", 2)[1], message.split(" ")[0].substring(1));
			else				
				userMessageBundle = new MessageBundle(client, message);
			server.push(userMessageBundle);
		}		
	}

	@Override
	public String requestNickname() {
		Scanner scanner = new Scanner(System.in);
		
		System.out.println("Enter Username: ");		
		return scanner.nextLine();
	}

	@Override
	public void error(String s) {
		System.err.println("Error: "+s);
	}

}
