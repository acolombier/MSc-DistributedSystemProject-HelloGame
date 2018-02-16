package Service;

import java.rmi.RemoteException;

import Controller.ClientInterface;
import Model.Message;

public class ClientImpl implements Client {
	
	private ClientInterface mInterface;
	private String mName;

	public ClientImpl(String name) {
		this.mName = name;
	}
	
	public ClientImpl(String name, ClientInterface c) {
		this.mName = name;
		this.mInterface = c;
	}
	
	public void setInterface(ClientInterface mInterface) {
		this.mInterface = mInterface;
	}

	@Override
	public String getName() throws RemoteException {
		return mName;
	}

	@Override
	public void send(Message m) throws RemoteException {
		mInterface.display_message(m);
	}

}
