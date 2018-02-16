package Service;

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

import Models.Message;
import Models.MessageBundle;

public class ServerImpl implements Server {
	
	public final int MAX_CACHE_SIZE = 100;
	
	private HashMap<String, Models.Client> mClients;
	private Queue<Message> mCacheMessages;
	private ObjectOutputStream mMessagesSaver;

	public ServerImpl(File f) throws IOException {
		super();
		this.mClients = new HashMap<>();
		this.mCacheMessages = new LinkedBlockingQueue<>();

		ObjectInputStream ois = new ObjectInputStream(new FileInputStream(f));

		try {
			while (true){
				mCacheMessages.add((Message) ois.readObject());
				
				if (mCacheMessages.size() > MAX_CACHE_SIZE)
						mCacheMessages.poll();
			}
		} catch (Exception e) {}
		
		mMessagesSaver = new ObjectOutputStream(new FileOutputStream(f));
		
	}
	
	private void saveMessage(Message m) throws IOException{
		mCacheMessages.add(m);
		
		if (mCacheMessages.size() > MAX_CACHE_SIZE)
				mCacheMessages.poll();
		mMessagesSaver.writeObject(m);
	}

	public void privateMessage(Message m){
		try {
			saveMessage(m);
			if (mClients.containsKey(m.getReceiver().getName()))
				try {
					mClients.get(m.getReceiver().getName()).getInterface().send(m);
				} catch (RemoteException e) {
					try {
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
			for (Iterator<Entry<String, Models.Client>> iterator = mClients.entrySet().iterator(); iterator.hasNext(); ) {
				Entry<String, Models.Client> c = iterator.next();
				if (m.getSender() != null && m.getSender().getName().equals(c.getKey()))
					continue;
				try {
					System.out.println("Sendind to "+c.getValue().toString());
					c.getValue().getInterface().send(m);
				} catch (RemoteException e) {
					try {
						this.unregister(c.getKey());
					} catch (RemoteException e1) {
						e1.printStackTrace();
					}
				}
			}
		} catch (IOException e2) {
			e2.printStackTrace();
		}
	}

	@Override
	public boolean register(Client c) throws RemoteException {
		if (mClients.containsKey(c.getName()))
			return false;
		
		mClients.put(c.getName(), new Models.Client(c.getName(), c));
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
		return mCacheMessages.toArray(new Message[mCacheMessages.size()]);
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
				r = new Message(null, m.getSender(), m.getSender()+ " is not connected on the server", Message.Type.ERROR);
			
			this.privateMessage(r);
			return null;
		}
		else if (m.getMessage().startsWith("/")){
			String[] payload = m.getMessage().substring(1).split(" ", 2);
			switch (Command.valueOf(payload[0].toUpperCase())){
			case HELP:
				this.privateMessage(new Message(null, m.getSender(), "/list\tGet the list of connected user\n/help\tDisplay the current help message", Message.Type.REGULAR));
				break;
			case LIST:
				String body = " "+Integer.valueOf(mClients.size())+" connected client(s): \n";
				for (String nickname: mClients.keySet())
					body += nickname+"\n";
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
		LIST, HELP;
	}
	
}
