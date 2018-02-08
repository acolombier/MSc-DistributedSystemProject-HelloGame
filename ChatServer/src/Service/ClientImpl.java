package Service;

import java.rmi.RemoteException;

import Controller.ClientInterface;
import Models.Message;

public class ClientImpl implements Client {
	
	private ClientInterface mInterface;
	private String mName;

	public ClientImpl(String name) {
		this.mName = name;
	}
	
	public void setInterface(ClientInterface mInterface) {
		this.mInterface = mInterface;
	}

	@Override
	public String getName() {
		return mName;
	}

	@Override
	public void send(Message m) throws RemoteException {
		mInterface.display_message(m);
	}

}
