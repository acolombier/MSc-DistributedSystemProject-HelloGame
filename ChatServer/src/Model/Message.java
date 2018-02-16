package Model;

import java.io.Serializable;
import java.util.Date;
import java.util.GregorianCalendar;

public class Message implements Serializable {
	private Client sender;
	private Client receiver;
	private String message;
	private long time;
	
	private Type mType;

	public Message(Client sender, Client receiver, String message, Type mType) {
		this.sender = sender;
		this.receiver = receiver;
		this.message = message;
		this.mType = mType;
		this.time = System.currentTimeMillis();
	}
	
	public Message(Client sender, Client receiver, String message) {
		this.sender = sender;
		this.receiver = receiver;
		this.message = message;
		this.mType = Type.REGULAR;
		this.time = System.currentTimeMillis();
	}


	public Type getType() {
		return mType;
	}

	public void setType(Type mType) {
		this.mType = mType;
	}
	
	@Override
	public String toString() {
		Date date = new Date(time);
		return "["+date.toString()+"] *"+(sender != null ? sender.getName() : "system")+"*"+(receiver != null ? "@"+receiver.getName():"")+": "+message;
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
		ERROR, DISCONNECT;
	}

	public static Message buildSystemMessage(String string, Type type) {
		Message m = new Message(null, null, string, type);
		System.out.println(m.toString());
		return m;
	}
}
