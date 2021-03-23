# HEAD FIRST: DESIGN PATTERN

## OO Basics

- Abstraction
- Encapsulation
- Polymorphism
- Inheritance

## OO Principles

- Encapsulate what varies.
- Favor composition over inheritance
- Program to interfaces, not implementations
- Strive for loosely coupled designs between objects that interact
- Classes should be open for extension but closed for modification
- Depend on abstractions. Do not depend on concrete classes.

## OO Patterns

**Strategy** - Defines a family of algorithms, encapsulates each one,
and makes them interchangeable.
Strategy lets the algorithm vary independently from clients that use it.

**Observer** - Defines a one-to-many dependency between objects
so that when one object changes state, all its dependents are
notified and updated automatically.

**Decorator** - Attach additional responsibilities to an object dynamically.
Decorators provide a flexible alternative to subclassing for extending functionality.

**Factory Method** - Defines an interface for creating an object, but let
subclasses decide which classes to instantiate. Factory Method lets a class
defer instantiation to the subclasses.

**Abstract Factory** - Provides an interface for creating families of related or
dependent objects without specifying their concrete classes.

**Singleton** - Ensure a class only has one instance and provide a global point of access to it.

**Command** - Encapsulates a request as an object, thereby letting you parametrize clients with different requests, queue or log requests, and support undoable operations.
