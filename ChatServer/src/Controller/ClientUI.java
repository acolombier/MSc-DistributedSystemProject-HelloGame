package Controller;

import Model.Message;
import UI.ChatServerUI;

public class ClientUI implements ClientInterface {
	
	@Override
	public void display_message(Message m) {
		// TODO Auto-generated method stub
		this.shiftMessages();
		ChatServerUI.getInstance().getMsgSender()[ChatServerUI.getInstance().getNumOfShownMsg() - 1].setText(m.getSender().getName());
		ChatServerUI.getInstance().getMsg()[ChatServerUI.getInstance().getNumOfShownMsg() - 1].setText(m.getMessage());
	}
	
	/*
	 * to add new message to the list we need to shift the latest 9 messages
	 */
	private void shiftMessages()
	{
		for(int i=0; i < ChatServerUI.getInstance().getNumOfShownMsg() - 1; i++) {
			ChatServerUI.getInstance().getMsgSender()[i].setText(ChatServerUI.getInstance().getMsgSender()[i+i].getText());
			ChatServerUI.getInstance().getMsg()[i].setText(ChatServerUI.getInstance().getMsg()[i+i].getText());
		}
	}


}
