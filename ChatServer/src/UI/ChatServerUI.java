package UI;

import java.awt.EventQueue;
import java.awt.FlowLayout;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JPanel;

import java.awt.BorderLayout;
import javax.swing.JTextField;
import javax.swing.ListSelectionModel;

import java.awt.Button;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.TextField;
import java.util.ArrayList;

public class ChatServerUI{

	private JFrame loginFrame;
	private JFrame chatFrame;
	private JButton connectButton;
	private JTextField usernameField;
	private JLabel[] msgSender;
	private JLabel[] msg;
	private JButton sendButton;
	private JTextField msgField;
	private JList clientsList;
	private final int numOfShownMsg = 10;
	
	
	/**
	 * Create the application.
	 */
	public ChatServerUI() {
		initialize();
		loginFrame.setVisible(true);
	}
	
	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		loginFrame = new JFrame();
		loginFrame.setTitle("Connect to Chat");
		loginFrame.setBounds(200, 200, 500, 400);
		loginFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		loginFrame.getContentPane().setLayout(null);
		
		JLabel titleLabel = new JLabel("Connect to Chat ...");
		titleLabel.setBounds(180, 20, 200, 50);
		Dimension d = new Dimension();
		d.setSize(300, 100);
		titleLabel.setSize(d);
		loginFrame.getContentPane().add(titleLabel);
		
		JLabel username = new JLabel("Username");
		username.setBounds(100, 150, 100, 40);
		loginFrame.getContentPane().add(username);
		
		usernameField = new JTextField();
		usernameField.setBounds(200, 155, 200, 25);
		loginFrame.getContentPane().add(usernameField);
		
		connectButton = new JButton("Connect");
		connectButton.setBounds(200, 250, 110, 25);
		loginFrame.getContentPane().add(connectButton);
		
		chatFrame = new JFrame();
		chatFrame.setBounds(100, 100, 800, 500);
		chatFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		chatFrame.getContentPane().setLayout(null);
		
		
//		JPanel panel = new JPanel( new BorderLayout() );
//		JPanel leftPanel = new JPanel();
//		JPanel rightPanel = new JPanel();
		
		msgSender = new JLabel[numOfShownMsg];
		msg = new JLabel[numOfShownMsg];
		for (int i=0; i< numOfShownMsg; i++) {
			msgSender[i] = new JLabel();
			msg[i] = new JLabel();
			msgSender[i].setBounds(50, i* 30 + 5, 150, 20);
			msg[i].setBounds(250, i* 30 + 5, 250, 20);
			chatFrame.getContentPane().add(msgSender[i]);
			chatFrame.getContentPane().add(msg[i]);
			
//			leftPanel.add(msgSender[i]);
//			rightPanel.add(msg[i]);
		}
		
//		panel.add(leftPanel, BorderLayout.WEST);
//		panel.add(rightPanel, BorderLayout.EAST);
//		panel.add(rightPanel, BorderLayout.SOUTH);
		
		
//		chatFrame.add(panel);
		
		sendButton = new JButton("Send");
		sendButton.setBounds(50, 400, 70, 25);
		chatFrame.getContentPane().add(sendButton);
		
		msgField = new JTextField();
		msgField.setBounds(150, 400, 250, 25);
		chatFrame.getContentPane().add(msgField);
		
		
//		clientsList = new JList(clientsListData);
//		clientsList.setSelectionMode(ListSelectionModel.SINGLE_INTERVAL_SELECTION);
//		clientsList.setLayoutOrientation(JList.HORIZONTAL_WRAP);
//		clientsList.setVisibleRowCount(-1);
//		chatFrame.getContentPane().add(clientsList);
	}
	
	public JFrame getChatFrame() {
		return chatFrame;
	}
	
	public JFrame getLoginFrame() {
		return loginFrame;
	}

	public JButton getConnectButton() {
		return connectButton;
	}

	public JTextField getUsernameField() {
		return usernameField;
	}

	public JLabel[] getMsgSender() {
		return msgSender;
	}
	
	public void setMsgSender(JLabel[] msgSender) {
		this.msgSender = msgSender;
	}

	public JLabel[] getMsg() {
		return msg;
	}

	public void setMsg(JLabel[] msg) {
		this.msg = msg;
	}

	public JButton getSendButton() {
		return sendButton;
	}

	public JTextField getMsgField() {
		return msgField;
	}

	public int getNumOfShownMsg() {
		return numOfShownMsg;
	}
	
	public JList getClientsList() {
		return clientsList;
	}
}
