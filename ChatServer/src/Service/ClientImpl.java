package Service;

import java.rmi.RemoteException;

import Controller.ClientInterface;
import Models.Message;

public class ClientImpl implements Client {
	
	private ClientInterface mInterface;

	public ClientImpl(ClientInterface mInterface) {
		super();
		this.mInterface = mInterface;
	}

	@Override
	public void send(Message m) throws RemoteException {
		mInterface.display_message(m);
	}

}
