package Models;

import java.io.Serializable;

public class MessageBundle implements Serializable {
	private Client mSender;
	private String mReceiver;
	private String mMessage;
	
	public MessageBundle(Client mSender, String mMessage, String mReceiver) {
		this.mSender = mSender;
		this.mMessage = mMessage;
		this.mReceiver = mReceiver;
	}
	
	public MessageBundle(Client mSender, String mMessage) {
		this.mSender = mSender;
		this.mMessage = mMessage;
		this.mReceiver = "";
	}

	public Client getSender() {
		return mSender;
	}

	public String getReceiver() {
		return mReceiver;
	}

	public String getMessage() {
		return mMessage;
	}
	
	
	
}
