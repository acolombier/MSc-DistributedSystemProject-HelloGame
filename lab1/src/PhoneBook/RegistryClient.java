package registry;
/*
 * Copyright (c) 1995, 2013, Oracle and/or its affiliates. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - Neither the name of Oracle or the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

import java.io.*;
import java.net.*;
import java.util.ArrayList;

import registry.*;

public class RegistryClient {
    public static void main(String[] argv) throws IOException {

        if (argv.length != 2) {
            System.err.println(
                "Usage: java RegistryClient <host name> <port number>");
            System.exit(1);
        }

        String hostName = argv[0];
        int portNumber = Integer.parseInt(argv[1]);

        try (
            Socket echoSocket = new Socket(hostName, portNumber);

            ObjectOutputStream out =
            new ObjectOutputStream(echoSocket.getOutputStream());

            ObjectInputStream in =
                new ObjectInputStream(echoSocket.getInputStream());


            BufferedReader stdIn =
                new BufferedReader(
                    new InputStreamReader(System.in))
        ) {
            out.flush();

            int userInput;
            while (true) {
                System.out.println(
                      "What do you want to do ? \n1 - Add an entry\n2 - Get an entry\n3 - List entries\n4 - Quit");
                userInput = Integer.valueOf(stdIn.readLine());

                ArrayList<Object> args = new ArrayList<>();

                switch (userInput){
                  case 1:{
                      System.out.println("What's their name ? ");
                      String fullname = stdIn.readLine();
                      System.out.println("What's their phone number ? ");
                      String phone = stdIn.readLine();
                      System.out.println("What's their email ? ");
                      String email = stdIn.readLine();

                      args.add(new Person(fullname, phone, email));
                      out.writeObject(new Command(Command.Type.ADD, args));

                      try {
                        Command result = (Command)in.readObject();

                        if (result.action() == Command.Type.SUCCESS)
                          System.out.println("Entry has been added");
                        else
                          System.out.println("Cannot add the entry: "+(String)result.objectAt(0));
                      } catch(ClassNotFoundException e){
                        System.out.println("Unknow object received");
                      }

                      break;
                    }
                  case 2:{
                      System.out.println("What's their name ? ");
                      String fullname = stdIn.readLine();

                      args.add(fullname);
                      out.writeObject(new Command(Command.Type.GET, args));

                      try {
                        Command result = (Command)in.readObject();
                        if (result.action() == Command.Type.SUCCESS) {
                            Person p = (Person)result.objectAt(0);
                            System.out.println("Entry: " + p);
                        }
                        else
                          System.out.println("Cannot add the entry: "+(String)result.objectAt(0));
                      } catch(ClassNotFoundException e){
                        System.out.println("Unknow object received");
                      }
                      break;
                    }
                  case 3:{
                      out.writeObject(new Command(Command.Type.LIST));

                      try {
                        Command result = (Command)in.readObject();
                        if (result.action() == Command.Type.SUCCESS) {
                          for (int i = 0; i < result.length(); i++){
                            Person p = (Person)result.objectAt(i);
                            System.out.println("Entry #" + String.valueOf(i + 1) + ": " + p);
                          }

                        }
                        else
                          System.out.println("Cannot get the entry list: "+(String)result.objectAt(0));
                      } catch(ClassNotFoundException e){
                        System.out.println("Unknow object received");
                      }
                      break;
                    }
                  default:
                    System.out.println("Please select in the range 1-3");
                    break;
                }
            }
        } catch (UnknownHostException e) {
            System.err.println("Don't know about host " + hostName);
            System.exit(1);
        } catch (IOException e) {
            System.err.println("Couldn't get I/O for the connection to " +
                hostName);
            System.exit(1);
        }
    }
}
