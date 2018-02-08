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
import java.util.Map;
import java.util.Queue;

import javax.tools.FileObject;

import Models.Message;
import Models.MessageBundle;

public class ServerImpl implements Server {
	
	public final int MAX_CACHE_SIZE = 100;
	
	private HashMap<String, Client> mClients;
	private Queue<Message> mCacheMessages;
	private ObjectOutputStream mMessagesSaver;

	public ServerImpl(File f) throws IOException {
		super();
		this.mClients = new HashMap<>();

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
					mClients.get(m.getReceiver().getName()).send(m);
				} catch (RemoteException e) {
					try {
						this.unregister(mClients.get(m.getReceiver().getName()));
					} catch (RemoteException e1) {
						e1.printStackTrace();
					}
				}
		} catch (IOException e2) {
			// TODO Auto-generated catch block
			e2.printStackTrace();
		}
	}
	
	public void broadcast(Message m){
		try {
			saveMessage(m);
			for (Map.Entry<String, Client> c: mClients.entrySet())
				if (!m.getSender().equals(c.getKey()))
					try {
						c.getValue().send(m);
					} catch (RemoteException e) {
						try {
							this.unregister(c.getValue());
						} catch (RemoteException e1) {
							e1.printStackTrace();
						}
					}
		} catch (IOException e2) {
			// TODO Auto-generated catch block
			e2.printStackTrace();
		}
	}

	@Override
	public boolean register(Client c) throws RemoteException {
		if (mClients.containsKey(c.getName()))
			return false;
		
		mClients.put(c.getName(), c);
		this.broadcast(Message.buildSystemMessage(c.getName() + " has joined the chat", Message.Type.CLIENT_CONNECTION_OR_LEAVING));
		return true;
	}

	@Override
	public void unregister(Client c) throws RemoteException {
		if (!mClients.containsKey(c.getName()))
			return;
		mClients.remove(c.getName());
		this.broadcast(Message.buildSystemMessage(c.getName() + " has left the chat", Message.Type.CLIENT_CONNECTION_OR_LEAVING));
		
	}

	@Override
	public Message[] pull() throws RemoteException {
		// TODO Auto-generated method stub
		return mCacheMessages.toArray(new Message[mCacheMessages.size()]);
	}

	@Override
	public Message push(MessageBundle m) throws RemoteException {
		// TODO Auto-generated method stub
		
		return null;
	}
	
}
