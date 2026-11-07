package com.example;

/**
 * This class prints a greeting message to the console.
 */
public class GreetingPrinter {

    /**
     * The entry point for this application.
     *
     * @param args command line arguments
     */
    public static void main(String[] args) {
        System.out.println("Hello World!");
    }

    /**
     * Prints a personalized greeting message to the console.
     *
     * @param name the person's name
     */
    public static void printPersonalizedGreeting(String name) {
        StringBuilder sb = new StringBuilder();
        sb.append("Hello, ");
        sb.append(name);
        System.out.println(sb.toString());
    }

    @Override
    public String toString() {
        return "GreetingPrinter []";
    }
}