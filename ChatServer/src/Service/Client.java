package Service;

import java.rmi.*;

import Models.Message;

public interface Client extends Remote {
	void send(Message m) throws RemoteException;
	String getName();
}