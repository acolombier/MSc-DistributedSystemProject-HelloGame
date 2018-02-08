package Service;

import java.rmi.RemoteException;
import java.util.ArrayList;
import java.util.HashMap;

import Models.Message;
import Models.MessageBundle;

public class ServerImpl implements Server {
	
	private HashMap<String, Client> mClients;

	public ServerImpl() {
		super();
		this.mClients = new HashMap<>();
	}

	@Override
	public boolean register(Client c) throws RemoteException {
		if (mClients.containsKey(c.getName()))
			return false;
		
		mClients.put(mClients.getName(), client);
		return true;
	}

	@Override
	public void unregister(Client c) throws RemoteException {
		// TODO Auto-generated method stub
		
	}

	@Override
	public ArrayList<Message> pull() throws RemoteException {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Message push(MessageBundle m) throws RemoteException {
		// TODO Auto-generated method stub
		return null;
	}
	
}
