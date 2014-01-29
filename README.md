sfb
===

An implementation of the Star Fleet Battles game in Python.

I wanted to test a few things:
 - REST done properly with resources, representations, content negotiation, simple vocabulary, content types and especially HATEOAS.
 - CORS
 - Separation of application logic from persistence. i.e. write application first, persist it independently.
 - SQLAlchemy
 - CouchDB
 - Single page application
 - SVG / HTML Canvas
 - JSON Schema
 - Prototype design pattern
 - Generic rules engine
 - Some other things that I can't remember

 
Some notes:
 - SFB has hundreds of pages of rules.  I wanted to be able to capture them succinctly.
 - I wanted parts of it to be sufficiently generic to be able to used for other games.
 - The jolly module is the more generic stuff.  The sfb module is specific to the SFB game.
