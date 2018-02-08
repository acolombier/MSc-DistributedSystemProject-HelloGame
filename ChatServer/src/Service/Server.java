package Service;

import java.rmi.*;
import java.util.ArrayList;
import Models.Message;
import Models.MessageBundle;

public interface Server extends Remote {
	boolean register(Client c) throws RemoteException;
	void unregister(Client c) throws RemoteException;
	Message[] pull() throws RemoteException;
	Message push(MessageBundle m) throws RemoteException;
}
