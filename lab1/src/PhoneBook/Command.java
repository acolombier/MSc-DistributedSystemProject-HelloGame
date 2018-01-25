package registry;

import java.io.Serializable;
import java.util.ArrayList;

public class Command implements Serializable {
  public enum Type {
    SUCCESS,
    FAIL,
    LIST,
    ADD,
    GET;
  }

  private Type mType;
  private ArrayList<Object> mObjects;

  public Command(Type type, ArrayList<Object> objects){
    this.mType = type;
    this.mObjects = objects;
  }

  public Command(Type type){
    this.mType = type;
    this.mObjects = new ArrayList<>();
  }

  public Type action() {
    return this.mType;
  }

  public Object objectAt(int i) {
    if (i < 0 || i >= mObjects.size())
      return null;
    return mObjects.get(i);
  }

  public int length() {
    return mObjects.size();
  }
}
