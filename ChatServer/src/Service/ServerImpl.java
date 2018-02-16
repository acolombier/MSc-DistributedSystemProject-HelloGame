package Service;

import java.awt.List;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.rmi.RemoteException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Queue;
import java.util.concurrent.LinkedBlockingQueue;

import javax.tools.FileObject;

import Model.Message;
import Model.MessageBundle;

public class ServerImpl implements Server {
	
	public final int MAX_CACHE_SIZE = 100;
	
	private HashMap<String, Model.Client> mClients;
	private ArrayList<Message> mMessages;
	private ObjectOutputStream mMessagesSaver;

	public ServerImpl(File f) throws IOException {
		super();
		this.mClients = new HashMap<>();
		this.mMessages = new ArrayList<>();

		ObjectInputStream ois = new ObjectInputStream(new FileInputStream(f));

		try {
			while (true)
				mMessages.add((Message) ois.readObject());
		} catch (Exception e) {}
		
		mMessagesSaver = new ObjectOutputStream(new FileOutputStream(f));
		
	}
	
	private void saveMessage(Message m) throws IOException{
		mMessages.add(m);
		mMessagesSaver.writeObject(m);
	}

	public void privateMessage(Message m){
		try {
			saveMessage(m);ArrayList<String> disconnectedClient = new ArrayList<>();
			
			if (mClients.containsKey(m.getReceiver().getName()))
				try {
					mClients.get(m.getReceiver().getName()).getInterface().send(m);
					if (m.getSender() != null)
						m.getSender().getInterface().send(m);
				} catch (RemoteException e) {
					try {
						m.getSender().getInterface().send(new Message(null, m.getSender(), m.getReceiver()+ " is not connected on the server", Message.Type.ERROR));
						this.unregister(m.getReceiver().getName());
					} catch (RemoteException e1) {
						e1.printStackTrace();
					}
				}
		} catch (IOException e2) {
			e2.printStackTrace();
		}
	}
	
	public void broadcast(Message m){
		try {
			saveMessage(m);
			
			ArrayList<String> disconnectedClient = new ArrayList<>();
			
			for (Iterator<Entry<String, Model.Client>> iterator = mClients.entrySet().iterator(); iterator.hasNext(); ) {
				Entry<String, Model.Client> c = iterator.next();
				
				try {
					System.out.println("Sendind to "+c.getValue().toString());
					c.getValue().getInterface().send(m);
				} catch (RemoteException e) {
					disconnectedClient.add(c.getKey());
				}
			}
			for (String c: disconnectedClient)
				try {
					this.unregister(c);
				} catch (RemoteException e1) {
					System.err.println("Could not kick the user "+c);
					e1.printStackTrace();
				}
		} catch (IOException e2) {
			e2.printStackTrace();
		}
	}

	@Override
	public boolean register(Client c) throws RemoteException {
		if (mClients.containsKey(c.getName()))
			return false;
		
		mClients.put(c.getName(), new Model.Client(c.getName(), c));
		Message m = Message.buildSystemMessage(c.getName() + " has joined the chat", Message.Type.CLIENT_CONNECTION_OR_LEAVING);
		this.broadcast(m);
		return true;
	}

	@Override
	public void unregister(String c) throws RemoteException {
		if (!mClients.containsKey(c))
			return;
		mClients.remove(c);
		this.broadcast(Message.buildSystemMessage(c + " has left the chat", Message.Type.CLIENT_CONNECTION_OR_LEAVING));
		
	}

	@Override
	public Message[] pull() throws RemoteException {
		return mMessages.toArray(new Message[mMessages.size()]);
	}

	@Override
	public Message push(MessageBundle m) throws RemoteException {
		if (mClients.containsKey(m.getSender().getName()) && mClients.get(m.getSender().getName()) == m.getSender())		
			return null;
		
		Message r;
		if (m.getReceiver() != null && m.getReceiver().length() > 0){
			if (mClients.containsKey(m.getReceiver()))
				r = new Message(mClients.get(m.getSender().getName()), mClients.get(m.getReceiver()), m.getMessage());
			else 
				r = new Message(null, m.getSender(), m.getReceiver()+ " is not connected on the server", Message.Type.ERROR);
			
			this.privateMessage(r);
			return null;
		}
		else if (m.getMessage().startsWith("/")){
			String[] payload = m.getMessage().substring(1).split(" ", 2);
			String body;
			switch (Command.valueOf(payload[0].toUpperCase())){
			case HELP:
				body = "\n";
				for (Command c: Command.values())
					body += "/"+c.name().toLowerCase()+c.getArgs()+"\t"+c.getDescription()+"\n";
				this.privateMessage(new Message(null, m.getSender(), body, Message.Type.REGULAR));
				break;
			case LIST:
				body = " "+Integer.valueOf(mClients.size())+" connected client(s): \n";
				for (String nickname: mClients.keySet())
					body += nickname+"\n";
				this.privateMessage(new Message(null, m.getSender(), body, Message.Type.REGULAR));
				break;
			case HISTORY:
				body = "";
				if (payload.length == 2){
					int c = 0, n = Integer.valueOf(payload[1]);
					n = n > 0  && n <= mMessages.size() ? n : mMessages.size();
	
					for (int i = mMessages.size(); i >= 0 && n > 0; i--){
						if (mMessages.get(i).getReceiver() == null || mMessages.get(i).getReceiver().equals(m.getSender())){
							body = "\t"+mMessages.get(i).toString()+"\n" + body;
							n--; c++;
						}
					}
				
					body = " "+Integer.valueOf(c)+" messages displayed";
				} else
					body = "\nUsage: /history <nb message>\n";
				this.privateMessage(new Message(null, m.getSender(), body, Message.Type.REGULAR));
				break;
			default:
				break;			
			}
			return null;
		}
		else
			r = new Message(m.getSender(), null, m.getMessage());
		
		System.out.println(r.toString());
		
		this.broadcast(r);
		return r;
	}
	
	public enum Command {
		LIST("Get the list of connected user"),
		HISTORY("Retrieve the last <n> messages from the history. 0 to get all of them", "<n>"), 
		HELP("Display the current help message"),
		QUIT("Leave the chat");

		private String desc;
		private String args;

		Command(String d){
			this.desc = d;	
			this.args = "";
		}
		Command(String d, String a){
			this.desc = d;	
			this.args = a;		
		}
		
		public String getArgs() {
			return " "+args;
		}
		
		public String getDescription() {
			return this.desc;
		}
	}
	
}
