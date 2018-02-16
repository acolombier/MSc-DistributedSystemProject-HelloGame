package Models;

import java.io.Serializable;

public class Client implements Serializable {
	
	private String mName;
	private Service.Client mInterface;

	public Client(String nickname) {
		this.mName = nickname;
	}
	
	public Client(String nickname, Service.Client inter) {
		this.mName = nickname;
		this.mInterface = inter;
	}
	
	
	public String getName() {
		return mName;
	}

	public Service.Client getInterface() {
		return mInterface;
	}


	public void setInterface(Service.Client mInterface) {
		this.mInterface = mInterface;
	}

	@Override
	public String toString(){
		return mName;
	}

	@Override
	public boolean equals(Object o){
		return o.getClass() == Client.class && ((Client)o).getName() == mName;
	}
}
