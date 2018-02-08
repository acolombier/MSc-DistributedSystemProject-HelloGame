package Models;

import java.io.Serializable;

import Models.Message.Type;

public class Message implements Serializable {
	private Client sender;
	private Client receiver;
	private String message;
	private long time;
	
	private Type mType;
	
	public Message(Client sender, Client receiver, String message, Type mType) {
		super();
		this.sender = sender;
		this.receiver = receiver;
		this.message = message;
		this.mType = mType;
		this.time = System.currentTimeMillis();
	}


	public Type getmType() {
		return mType;
	}



	public void setmType(Type mType) {
		this.mType = mType;
	}



	public Client getSender() {
		return sender;
	}



	public Client getReceiver() {
		return receiver;
	}



	public String getMessage() {
		return message;
	}



	public long getTime() {
		return time;
	}



	public enum Type {
		REGULAR,
		CLIENT_CONNECTION_OR_LEAVING,
		ERROR;
	}



	public static Message buildSystemMessage(String string, Type type) {
		return new Message(null, null, string, type);
	}
}
