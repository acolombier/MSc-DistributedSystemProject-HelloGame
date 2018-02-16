package Controller;

import java.rmi.RemoteException;

import Model.Message;
import Service.Server;

public interface ClientInterface {
	void display_message(Message m);
	void run(Server server, Model.Client client) throws RemoteException;
	String requestNickname();
	void error(String s);
}
