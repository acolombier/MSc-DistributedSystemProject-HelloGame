package Models;

public class Client {
	
	private String mName;

	public Client(String nickname) {
		this.mName = nickname;
	}
	
	
	public String getName() {
		return mName;
	}

	@Override
	public boolean equals(Object o){
		return o.getClass() == Client.class && ((Client)o).getName() == mName;
	}
}
