package registry;

import java.io.Serializable;

public class Person implements Serializable {
  protected String fullname;
  protected String phonenum;
  protected String email;

  public Person(String fullname, String phonenum, String email){
    this.fullname = fullname;
    this.phonenum = phonenum;
    this.email = email;
  }

  public String toString(){
    return this.fullname + " - Phone: " + this.phonenum + " - Email: " + this.email;
  }

}
