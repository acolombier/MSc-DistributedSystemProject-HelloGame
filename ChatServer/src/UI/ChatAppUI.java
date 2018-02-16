package UI;

import java.awt.EventQueue;

import javax.swing.JFrame;
import java.awt.BorderLayout;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.BoxLayout;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JButton;

public class ChatAppUI {

	private JFrame frmChatApp;
	private JTextField messageField;
	private JTextArea chatBox;
	private JButton sendButton;
	private JScrollPane mScroll;
	
	/**
	 * Create the application.
	 */
	public ChatAppUI() {
		initialize();
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frmChatApp = new JFrame();
		frmChatApp.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frmChatApp.setTitle("Chat App");
		frmChatApp.setBounds(100, 100, 450, 300);
		frmChatApp.getContentPane().setLayout(new BorderLayout(0, 0));
		
		chatBox = new JTextArea();
		chatBox.setEditable(false);
		mScroll = new JScrollPane(chatBox);
		frmChatApp.getContentPane().add(mScroll);
		
		JPanel panel = new JPanel();
		frmChatApp.getContentPane().add(panel, BorderLayout.SOUTH);
		panel.setLayout(new BorderLayout(0, 0));
		
		sendButton = new JButton("Send");
		sendButton.setEnabled(false);
		panel.add(sendButton, BorderLayout.EAST);
		
		messageField = new JTextField();
		messageField.setEnabled(false);
		panel.add(messageField, BorderLayout.CENTER);
		messageField.setColumns(10);
	}

	public JTextField getMessageField() {
		return messageField;
	}

	public JTextArea getChatBox() {
		return chatBox;
	}

	public JButton getSendButton() {
		return sendButton;
	}

	public JFrame getMainFrame() {
		return frmChatApp;
	}

	public void scrollDown() {
		mScroll.getVerticalScrollBar().setValue(mScroll.getVerticalScrollBar().getMaximum());
	}
	
	
}
