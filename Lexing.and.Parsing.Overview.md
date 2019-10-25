[]{#___top .dummyTopAnchor}

::: {.toc_title}
An Overview of Lexing and Parsing
:::

### 

::: {.toc_toc}
Table of contents
:::

  -------------------------------------------------------------------------------------------------
               [An Overview of Lexing and Parsing](#An_Overview_of_Lexing_and_Parsing)
                  [A History Lesson - In Absentia](#A_History_Lesson_-_In_Absentia)
              [But Why Study Lexing and Parsing?](#But_Why_Study_Lexing_and_Parsing%3F)
         [Good Solutions and Home-grown Solutions](#Good_Solutions_and_Home-grown_Solutions)
                   [The Lexer\'s Job Description](#The_Lexer%27s_Job_Description)
                  [The Parser\'s Job Description](#The_Parser%27s_Job_Description)
                       [Grammars and Sub-grammars](#Grammars_and_Sub-grammars)
                               [Sub-grammar \# 1](#Sub-grammar_%23_1)
                               [Sub-grammar \# 2](#Sub-grammar_%23_2)
            [My Golden Rule of Lexing and Parsing](#My_Golden_Rule_of_Lexing_and_Parsing)
   [In Case You Think This is Going to be Complex](#In_Case_You_Think_This_is_Going_to_be_Complex)
                                [Coding the Lexer](#Coding_the_Lexer)
                    [Back to the Finite Automaton](#Back_to_the_Finite_Automaton)
                                          [States](#States)
                               [Sample Lexer Code](#Sample_Lexer_Code)
                    [Coding the Lexer - Revisited](#Coding_the_Lexer_-_Revisited)
                               [Coding the Parser](#Coding_the_Parser)
                              [Sample Parser Code](#Sample_Parser_Code)
         [Connecting the Parser back to the Lexer](#Connecting_the_Parser_back_to_the_Lexer)
    [Something Fascinating about Rule Descriptors](#Something_Fascinating_about_Rule_Descriptors)
                                [Chains and Trees](#Chains_and_Trees)
                       [Less Coding - More Design](#Less_Coding_-_More_Design)
   [My Rules-of-Thumb for Writing Lexers/Parsers](#My_Rules-of-Thumb_for_Writing_Lexers%2FParsers)
                   [Eschew Premature Optimisation](#Eschew_Premature_Optimisation)
                              [Divide and Conquer](#Divide_and_Conquer)
                      [Don\'t Reinvent the Wheel](#Don%27t_Reinvent_the_Wheel)
                         [Be Patient with the STT](#Be_Patient_with_the_STT)
                     [Be Patient with the Grammar](#Be_Patient_with_the_Grammar)
                    [Wrapping Up and Winding Down](#Wrapping_Up_and_Winding_Down)
                                          [Author](#Author)
                                         [Licence](#Licence)
  -------------------------------------------------------------------------------------------------

[An Overview of Lexing and Parsing](#___top "click to go to top of document"){#An_Overview_of_Lexing_and_Parsing .u}
====================================================================================================================

For a more formal discussion than this article of what exactly lexing
and parsing are, start with Wikipedia\'s definitions:
[Lexing](http://en.wikipedia.org/wiki/Lexing){.podlinkurl} and
[Parsing](http://en.wikipedia.org/wiki/Parsing){.podlinkurl}.

Also, the word parsing sometimes includes lexing and sometimes doesn\'t.
This can cause confusion, but I\'ll try to keep them clear. Such
situations arise with other words, and our minds usually resolve the
specific meaning intended by analysing the context in which the word is
used. So, keep your mind in mind.

[A History Lesson - In Absentia](#___top "click to go to top of document"){#A_History_Lesson_-_In_Absentia .u}
==============================================================================================================

At this point, an article such as this would normally provide a summary
of historical developments in this field, as in \'how we got to here\'.
I won\'t do that, especially as I first encountered parsing many years
ago, when the only tools (lex, bison, yacc) were so complex to operate I
took the pledge to abstain. Nevertheless, it\'s good to know such tools
are still available, so here are a few references:

[Flex](http://directory.fsf.org/wiki/Flex){.podlinkurl} is a successor
to
[lex](http://en.wikipedia.org/wiki/Lex_programming_tool){.podlinkurl},
and [Bison](http://www.gnu.org/software/bison/){.podlinkurl} is a
successor to [yacc](http://en.wikipedia.org/wiki/Yacc){.podlinkurl}.
This article explains why I (still) don\'t use any of these.

[But Why Study Lexing and Parsing?](#___top "click to go to top of document"){#But_Why_Study_Lexing_and_Parsing? .u}
====================================================================================================================

There are many situations where the only path to a solution requires a
lexer and a parser.

The lex phase and the parse phase can be combined into a single process,
but I advocate always keeping them separate, and I aim below to
demonstrate why this is the best policy.

Also, for beginners, note that the phases very conveniently run in
alphabetical order: We lex and then we parse.

So, let\'s consider some typical situations where lexing and parsing are
the tools needed:

[1: Running a program]{#1:_Running_a_program}

:   This is trivial to understand, but not to implement. In order to run
    a program we need to set up a range of pre-conditions:

    [o Define the language, perhaps called Perl]{#o_Define_the_language,_perhaps_called_Perl}

    :   

    [o Write a compiler (combined lexer and parser) for that language\'s grammar]{#o_Write_a_compiler_(combined_lexer_and_parser)_for_that_language's_grammar}

    :   

    [o Write a program in that language]{#o_Write_a_program_in_that_language}

    :   

    [o *Lex and parse* the source code]{#o_Lex_and_parse_the_source_code}

    :   After all, it must be syntactically correct before we run it. If
        not, we display syntax errors.

        The real point of this step is to determine the programmer\'s
        *intention*, i.e. what is the reason for writing the code? Not
        to run it actually, but to get the output. And how do we do
        that?

    [o Run the code]{#o_Run_the_code}

    :   Then we can gaze at the output which, hopefully, is correct. Or,
        perhaps, we are confronted by logic errors.

[2: Rendering a web page of HTML + Content]{#2:_Rendering_a_web_page_of_HTML_+_Content}

:   The steps are identical to the above, with HTML replacing Perl,
    althought I can\'t bring myself to call writing HTML writing a
    program.

    This time, we\'re asking: What is the web page designer\'s
    *intention*, i.e. how exactly do they want the page to be rendered?

    Of course, syntax checking is far looser than with a programming
    language, but must still be undertaken. For instance, here\'s an
    example of clearly-corrupt HTML which can be parsed by
    [Marpa](http://jeffreykegler.github.com/Marpa-web-site/){.podlinkurl}:

                <title>Short</title><p>Text</head><head>

    See
    [Marpa::R2::HTML](http://metacpan.org/module/Marpa::R2::HTML){.podlinkpod}
    for details. The original version of Marpa has been superceded by
    Marpa::R2. Now I use
    [Marpa::R2](http://metacpan.org/module/Marpa::R2){.podlinkpod} in
    all my work (which happens to not involve HTML).

[3: Rendering an image, perhaps in SVG]{#3:_Rendering_an_image,_perhaps_in_SVG}

:   Consider this file, written in the
    [DOT](http://www.graphviz.org/content/dot-language){.podlinkurl}
    language, as used by the
    [Graphviz](http://www.graphviz.org/){.podlinkurl} graph visualizer
    (*teamwork.dot*):

                digraph Perl
                {
                graph [ rankdir="LR" ]
                node  [ fontsize="12pt" shape="rectangle" style="filled, solid" ]
                edge  [ color="grey" ]
                "Teamwork" [ fillcolor="yellow" ]
                "Victory"  [ fillcolor="red" ]
                "Teamwork" -> "Victory" [ label="is the key to" ]
                }

    Here we have a \'program\' and we wish to give effect to the
    author\'s *intention* by rendering this as an image:

    ![](http://savage.net.au/Ron/html/graphviz2.marpa/teamwork.svg)

    What\'s required to do that? As above, *lex, parse*, render. Using
    Graphviz\'s *dot* command to carry out these 3 tasks, we would run:

                shell> dot -Tsvg teamwork.dot > teamwork.svg

    Note: Files used in these examples can be downloaded from
    <http://savage.net.au/Ron/html/graphviz2.marpa/teamwork.tgz>.

    Now, the above link to the DOT language points to a definition of
    DOT\'s syntax, written in a somewhat casual version of BNF:
    [Backus-Naur
    Form](http://en.wikipedia.org/wiki/Backus%E2%80%93Naur_Form){.podlinkurl}.
    This is significant, since it\'s usually straight-forward to
    translate a BNF description of a language into code within a lexer
    and parser.

[4: Rendering that same image, using a different language in the input file]{#4:_Rendering_that_same_image,_using_a_different_language_in_the_input_file}

:   Let\'s say we feel the Graphviz language is too complex, and hence
    we write a wrapper around it, so end users can code in a simplified
    version of that language. This has been done, with the original
    effort available in the now-obsolete Perl module
    [Graph::Easy](http://metacpan.org/module/Graph::Easy){.podlinkpod}.
    Tels, the author, devised his own very clever [little
    language](http://en.wikipedia.org/wiki/Little_languages){.podlinkurl},
    which he called Graph::Easy. The manual for that is on-line
    [here](http://bloodgate.com/perl/graph/manual/){.podlinkurl}.

    When I took over maintenance of
    [Graph::Easy](http://metacpan.org/module/Graph::Easy){.podlinkpod},
    I found the code too complex to read, let alone work on, so I wrote
    another implementation of the lexer and parser, released as
    [Graph::Easy::Marpa](http://metacpan.org/module/Graph::Easy::Marpa){.podlinkpod}.
    I\'ll have much more to say about that in the next article in this
    2-part series, so for now we\'ll just examine the above graph
    re-cast in Graph::Easy (*teamwork.easy*):

                graph {rankdir: LR}
                node {fontsize: 12pt; shape: rectangle; style: filled, solid}
                edge {color: grey}
                [Teamwork]{fillcolor: yellow}
                -> {label: is the key to}
                [Victory]{fillcolor: red}

    Simpler for sure, but how does
    [Graph::Easy::Marpa](http://metacpan.org/module/Graph::Easy::Marpa){.podlinkpod}
    work? As always: *lex, parse*, render. More samples of
    [Graph::Easy::Marpa](http://metacpan.org/module/Graph::Easy::Marpa){.podlinkpod}\'s
    work are
    [here](http://savage.net.au/Perl-modules/html/graph.easy.marpa/index.html){.podlinkurl}.

It should be clear by now that lexing and parsing are in fact
widespread, although they often operate out of sight, with just their
rendered output visible to the average programmer and web surfer.

What all such problems have in common is complex but well-structured
source text formats, with a bit of hand-waving over the tacky details
available to authors of documents in HTML. And, in each case, it is the
responsibility of the programmer writing the lexer and parser to honour
the intention of the original text\'s author.

And we can only do that by recognizing each token in the input as
embodying some meaning (e.g. a word such as \'print\' *means* output
something of the author\'s choosing), and bringing that meaning to
fruition (make the output visible on a device).

With all that I can safely claim that it\'s the ubiquity and success of
lexing and parsing which justify their recognition as vital constituents
in the world of software engineering. And with that we\'re done
answering the question posed above: Why study them?

[Good Solutions and Home-grown Solutions](#___top "click to go to top of document"){#Good_Solutions_and_Home-grown_Solutions .u}
================================================================================================================================

But there\'s another - significant - reason to discuss lexing and
parsing. And that\'s to train programmers, without expertise in such
matters, to resist the understandable urge to opt for using tools they
are already familiar with, with regexps being the \'obvious\' choice.

Sure, regexps suit many simple cases, and the old standbys of flex and
bison are always available, but now there\'s a new kid on the block:
[Marpa](http://www.jeffreykegler.com/marpa){.podlinkurl}.

Marpa is heavily based on theoretical work done over many decades, and
comes in various forms:

[o libmarpa]{#o_libmarpa}

:   Hand-crafted in C.

[o Marpa::XS]{#o_Marpa::XS}

:   The Perl and C-based interface to the *previous* version of
    libmarpa.

[o Marpa::R2]{#o_Marpa::R2}

:   The Perl and C-based interface to the most recent version of
    libmarpa. This is the version I use.

[o Marpa::R2::Advanced::Thin]{#o_Marpa::R2::Advanced::Thin}

:   The newest and thinnest interface to libmarpa, which documents how
    to make Marpa accessible to non-Perl languages.

The problem, of course, is whether or not any of these are a good, or
even excellent, choice.

Marpa\'s advantages are huge, and can be summarized as:

[o Is well tested]{#o_Is_well_tested}

:   This alone is of great significance.

[o Has a Perl interface]{#o_Has_a_Perl_interface}

:   This means I can specify the task in Perl, and let Marpa handle the
    details.

[o Has its own Google Group]{#o_Has_its_own_Google_Group}

:   See <http://groups.google.com/group/marpa-parser?hl=en>

[o Is already used by various modules on]{#o_Is_already_used_by_various_modules_on_CPAN_(this_search_keyed_to_Marpa)}[CPAN](https://metacpan.org/search?q=Marpa){.podlinkurl} (this search keyed to Marpa)

:   Hence, Open Source says you can see exactly how other people use it.

[o Has a very simple syntax]{#o_Has_a_very_simple_syntax}

:   Once you get used to it, of course! And if you\'re having trouble,
    just post on the Google Group.

    Actually, if you\'ve ever worked with flex and bison, you\'ll be
    astonished at how simple it is to drive Marpa.

[o Is very fast (libmarpa is written in C)]{#o_Is_very_fast_(libmarpa_is_written_in_C)}

:   This is a bit surprising, since new technology usually needs some
    time to surpass established technology while delivering the
    all-important stability.

[o Is being improved all the time]{#o_Is_being_improved_all_the_time}

:   For instance, recently the author eliminated the dependency on Glib,
    to improve portability.

    What\'s important is that this work is on-going, and we can expect a
    series of incremental improvements for some time to come.

So, some awareness of the choice of tools is important long before
coding begins.

BTW: I use Marpa in
[Graph::Easy::Marpa](http://metacpan.org/module/Graph::Easy::Marpa){.podlinkpod}
and
[GraphViz2::Marpa](http://metacpan.org/module/GraphViz2::Marpa){.podlinkpod}.

However, this is not an article on Marpa (but the next one is), so
let\'s return to discussing lexing and parsing.

[The Lexer\'s Job Description](#___top "click to go to top of document"){#The_Lexer's_Job_Description .u}
=========================================================================================================

As mentioned, the stages, conveniently, run in English alphabetical
order, so we lex and then we parse.

Here, I\'m using lexing to mean the comparatively simple process of
tokenising a stream of text, which means chopping that input stream into
discrete tokens, and identifying the type of each token. The output is a
new stream, this time of stand-alone tokens. And I say \'comparatively\'
because I see parsing as complex *compared to* lexing.

And no, lexing does not do anything more than identify tokens. Therefore
questions about the meanings of those tokens, or their acceptable order,
are matters for the parser.

So, the lexer will say: I have found another token, and have identified
it as being of some type T. Hence, for each recognized token, 2 items
will be output:

[o The type of the token]{#o_The_type_of_the_token}

[o The value of the token]{#o_The_value_of_the_token}

Since the process happens repeatedly, the output will be an array of
token elements, with each element needing at least these 2 components:
type and value.

In practice, I prefer to represent these elements as a hashref, like
this:

            {
                    count => $integer, # 1 .. N.
                    name  => '',       # Unused.
                    type  => $string,  # The type of the token.
                    value => $value,   # The value from the input stream.
            }

with the array being managed by an object of type
[Set::Array](http://metacpan.org/module/Set::Array){.podlinkpod}, which
I did not write but which I do now maintain. The advantage of Set::Array
over [Set::Tiny](http://metacpan.org/module/Set::Tiny){.podlinkpod} is
that the former preserves the ordering of the elements. See also [this
report](http://savage.net.au/Perl-modules/html/setops.report.html){.podlinkurl}
comparing a range of set-handling modules.

The \'count\' field, apparently redundant, is sometimes employed in the
clean-up phase of the lexer, which may need to combine tokens
unnecessarily split by the regexp-based approach. Also, it is available
to the parser if needed, so I always include it in the hashref.

The \'name\' field really is unused, but gives people who fork or
sub-class my code a place to work with their own requirements, without
worrying that their edits will affect the fundamental code.

BTW, if you have an application where the output is best stored in a
tree, the Perl module
[Tree::DAG\_Node](http://metacpan.org/module/Tree::DAG_Node){.podlinkpod}
is superb (and which I also did not write but now maintain).

[The Parser\'s Job Description](#___top "click to go to top of document"){#The_Parser's_Job_Description .u}
===========================================================================================================

The parser then, concerns itself with the context in which each token
appears, which is a way of saying it cares about whether or not the
sequence and combination of tokens actually detected fits the expected
grammar.

Ideally, the grammar is provided in BNF Form. This makes it easy to
translate into the form acceptable to Marpa. If it\'s not in that form,
you\'re work is (probably) going to be harder, simply because someone
else has *not* done the hard work formalizing the grammar.

And now it\'s time to expand on \'grammars\'.

[Grammars and Sub-grammars](#___top "click to go to top of document"){#Grammars_and_Sub-grammars .u}
====================================================================================================

An example grammar was mentioned above:
[DOT](http://www.graphviz.org/content/dot-language){.podlinkurl}. But,
how are we to understand a block of text written in BNF? Well, training
is of course required when taking on such a task, and to that I\'d add
what I\'ve gleaned from this work, as follows.

To us beginners eventually comes the realization that grammars, no
matter how formally defined or otherwise, contain within them 2
sub-grammars:

[Sub-grammar \# 1](#___top "click to go to top of document"){#Sub-grammar_#_1 .u}
---------------------------------------------------------------------------------

One sub-grammar specifies what a token looks like, meaning what range of
forms it can assume in the input stream. If an incomprehensible
candidate it detected, the lexer can generate an error, or it can
activate a strategy called - by Jeffrey Kegler, the author of
[Marpa](http://www.jeffreykegler.com/marpa){.podlinkurl} - [Ruby
Slippers](http://blogs.perl.org/users/jeffrey_kegler/2011/11/marpa-and-the-ruby-slippers.html){.podlinkurl}
(which has no relation to the Ruby programming language).

Put simply, the Ruby Slippers strategy fiddles the current token, or
perhaps an even larger section of the input stream, in a way that
satisfies the grammar, and restarts processing at the new current token.
Marpa is arguably unique in being able to do this.

[Sub-grammar \# 2](#___top "click to go to top of document"){#Sub-grammar_#_2 .u}
---------------------------------------------------------------------------------

The other sub-grammar specifies how these tokens are allowed to combine,
meaning if they don\'t conform to the grammar, the code generates a
syntax error of some sort.

[My Golden Rule of Lexing and Parsing](#___top "click to go to top of document"){#My_Golden_Rule_of_Lexing_and_Parsing .u}
--------------------------------------------------------------------------------------------------------------------------

It is: *We will encode the first sub-grammar into the lexer and the
second into the parser.*

This says that if we know what tokens look like, we can tokenize the
input stream, i.e. split it into separate tokens using a lexer. Then we
give those tokens to the parser for (more) syntax checking, and for
interpretation of what the user presumably intended with that specific
input stream (combination of tokens).

And that gives us a clear plan-of-attack when confronted by a new
project.

[In Case You Think This is Going to be Complex](#___top "click to go to top of document"){#In_Case_You_Think_This_is_Going_to_be_Complex .u}
============================================================================================================================================

Truely, it just *sounds* complicated, because I\'ll be introducing
various presumably-new concepts, but don\'t dispair. It\'s not really
that difficult.

We have to, somehow and somewhere, manage the complexity of the question
\'Is this a valid document?\' for a given grammar.

Recognizing a token with a regex is easy. Keeping track of the context
in which we see that token, and the context in which our grammar allows
that token, are hard.

Yes, the complexity of setting up and managing a formal grammar and the
DFA (see below) seems like a lot of work, but it\'s a specified and well
understood mechanism we don\'t have to reinvent something every time.

By limiting the code we have to write two things: a set of rules for how
to construct tokens within a grammar, and a set of rules for what
happens when we construct a valid combination of tokens, we can focus on
the important part of our application - determining what a document
which conforms to the grammar means (the author\'s *intention*) - and
less on the mechanics of verifying that a document matches the grammar.

[Coding the Lexer](#___top "click to go to top of document"){#Coding_the_Lexer .u}
==================================================================================

Here\'s how it works: The lexer\'s job is to recognise tokens, and our
sub-grammar \#1 specifies what they look like. So our lexer will have to
examine the input stream, possibly one character at a time, to see if
the \'current\' input, appended to the immediately preceding input, fits
the definition of a token.

Now, a programmer can write a lexer anyway they want of course. The way
I do it is with regexps combined with a DFA ([Discrete Finite
Automaton](http://en.wikipedia.org/wiki/Deterministic_finite_automaton){.podlinkurl})
module. This blog entry - [More Marpa
Madness](http://blogs.perl.org/users/andrew_rodland/2012/01/more-marpa-madness.html){.podlinkurl}
- discusses using Marpa in the lexer (i.e. as well as in the parser,
which is where I use it).

And what is a DFA? Abusing any reasonable definition, let me describe
them thusly: The \'Finite\' part means the input stream only contains a
limited number of different tokens, which simplifies the code, and the
\'Automata\' in our case is the software machine we are writing, i.e.
the program. For more, see that Wikipedia article on DFAs. BTW: DFAs are
often known by their nick, STT (State Transition Table).

And now, what\'s this [State Transition Table
(STT)](http://en.wikipedia.org/wiki/State_transition_table){.podlinkurl}?
It is precisely the set of regexps which recognise tokens, together with
instructions about what to do when a specific type of token is
recognised.

But how do we make this all work?
[MetaCPAN](https://metacpan.org/){.podlinkurl} is your friend! In
particular, we\'ll use
[Set::FA::Element](http://metacpan.org/module/Set::FA::Element){.podlinkpod}
to drive the process. For candidate alternatives I assembled a list of
Perl modules with relevance in the area, while cleaning up the docs for
Set::FA. See <https://metacpan.org/module/Set::FA#See-Also>. I did not
write [Set::FA](http://metacpan.org/module/Set::FA){.podlinkpod}, nor
[Set::FA::Element](http://metacpan.org/module/Set::FA::Element){.podlinkpod},
but I now maintain them.

Be assured, such a transformation of BNF (or whatever our grammar\'s
source is) into a DFA gives us:

[o Insight into the problem]{#o_Insight_into_the_problem}

:   To cast BNF into regexps means we must understand exactly what the
    grammar definition is saying.

[o Clarity of formulation]{#o_Clarity_of_formulation}

:   We end up with a spreadsheet which simply and clearly encodes our
    understanding of tokens.

    Spreadsheet? Yes, I store the derived regexps, along with other
    information, in a spreadsheet, as explained below. Techniques for
    incorporating this spreadsheet into the source code are discussed
    shortly.

[Back to the Finite Automaton](#___top "click to go to top of document"){#Back_to_the_Finite_Automaton .u}
==========================================================================================================

In practice, we simply read and re-read, many times, the definition of
our BNF (here the
[DOT](http://www.graphviz.org/content/dot-language){.podlinkurl}
language), and build up the corresponding set of regexps to handle each
\'case\'. This is labourious work, no doubt about it.

For example, by using a regexp like /\[a-zA-Z\_\]\[a-zA-Z\_0-9\]\*/, we
can get Perl\'s regexp engine to intelligently gobble up characters as
long as they fit the definition. Here, the regexp is just saying: Start
with a letter, upper- or lower-case, or an underline, followed by 0 or
more letters, digits or underlines. Look familiar? It\'s very close to
the Perl definition of \\w, but disallows leading digits. Actually,
[DOT](http://www.graphviz.org/content/dot-language){.podlinkurl}
disallows them (in certain circumstances), so we have to, but of course
it (DOT) does allow pure numbers in certain circumstances.

And what do we do with all these hand-crafted regexps? We use them as
*data* to feed into the DFA, along with the input stream. The output of
the DFA is basically a flag saying Yes/No, the input stream
matches/doesn\'t match the token definitions specified by the given
regexps. Along the way, the DFA calls one of our callback functions each
time a token is successfully recognized, so we can stockpile them. Then,
at the end of the run, we can output them as a stream of tokens, each
with its identifying \'type\', as per \'The Lexer\'s Job Description\'
above.

A note about callbacks: Sometimes it\'s easier to design a regexp to
capture more than seems appropriate, and to use code in the callback to
chop up what\'s been captured, outputting several token elements as a
consequence.

Since developing the STT is such an iterative process, you\'ll want
various test files, and some scripts with short names to run the tests.
Short names because you\'re going to be running these scripts an
unbelievable number of times\....

[States](#___top "click to go to top of document"){#States .u}
==============================================================

So, what are states and why do we care about them?

Well, at any instant our STT (automation, software machine) is in
precisely 1 (one) state. Perhaps it has not yet received even 1 token
(it\'s in the \'start\' state), or perhaps it has just finished
processing the previous one. Whatever, the code maintains information so
as to know exactly what state it is in, and this leads to knowing
exactly what set of tokens is now acceptable. I.e. any one of this set
will be a legal token in the current state.

This is telling us then that we have to associate each regexp with a
specific state, and visa versa, and it\'s implicitly telling us that we
stay in the current state as long as each new input character matches a
regexp belonging to the current state, and that we jump (transition) to
a new state when that character does not match.

[Sample Lexer Code](#___top "click to go to top of document"){#Sample_Lexer_Code .u}
====================================================================================

Consider this simplistic code from the synopsis of
[Set::FA::Element](http://metacpan.org/module/Set::FA::Element){.podlinkpod}:

            my($dfa) = Set::FA::Element -> new
            (
                    accepting   => ['baz'],
                    start       => 'foo',
                    transitions =>
                    [
                            ['foo', 'b', 'bar'],
                            ['foo', '.', 'foo'],
                            ['bar', 'a', 'foo'],
                            ['bar', 'b', 'bar'],
                            ['bar', 'c', 'baz'],
                            ['baz', '.', 'baz'],
                    ],
            );

In the *transitions* parameter the first line says: \'foo\' is a
state\'s name, and \'b\' is a regexp saying we jump to state \'bar\' if
the next input char is \'b\'. And so on.

This in turn tells us that to use
[Set::FA::Element](http://metacpan.org/module/Set::FA::Element){.podlinkpod}
we have to prepare a transitions parameter matching this format. Hence
the need for states and regexps.

And this is code I\'ve used, taken directly from
[GraphViz2::Marpa::Lexer::DFA](http://metacpan.org/module/GraphViz2::Marpa::Lexer::DFA){.podlinkpod}:

            Set::FA::Element -> new
            (
                    accepting   => \@accept,
                    actions     => \%actions,
                    die_on_loop => 1,
                    logger      => $self -> logger,
                    start       => $self -> start,
                    transitions => \@transitions,
                    verbose     => $self -> verbose,
            );

Let\'s discuss these parameters.

[o accepting]{#o_accepting}

:   This is an arrayref of state names, meaning that, after processing
    the entire input stream, if we end up in one of these states, then
    we have \'accepted\' that input stream. That just means that every
    input token matched an appropriate regexp, where \'appropriate\'
    means every char matched the regexp belonging to the current state,
    whatever the state was at the instant that char was input.

[o actions]{#o_actions}

:   This is a hashref of function names, so we can call a function,
    optionally, upon entering or leaving any state. That\'s how we
    stockpile recognized tokens.

    Further, since we write these functions, and we attach each to a
    particular combination of state and regexp, we encode into the
    function the knowledge of what \'type\' of token has just been
    matched when the DFA calls a function. And that\'s how our stockpile
    will end up with (token, type) pairs to output at the end of the
    run.

[o die\_on\_loop]{#o_die_on_loop}

:   This flag, if true, tells the DFA to stop if none of the regexps
    belonging to the current state match the current input char, i.e.
    stop rather than loop for ever.

    You might wonder what stopping automatically is not the default, or
    even mandatory. Well, it\'s because you might was to try some
    recovery algorithm in such a situation, before dying.

[o logger]{#o_logger}

:   This is an (optional) logger objct.

[o start]{#o_start}

:   This is the name of the state in which the STT starts, so the code
    knows which regexp(s) to try upon inputting the very first char.

[o transitions]{#o_transitions}

:   This is a potentially large arrayref, listing separately for all
    states all the regexps which are to be invoked, one at a time, in
    the current state, while trying to match the current input char.

[o verbose]{#o_verbose}

:   Specifies how much to report if the logger object is not defined.

So, the next problem is how to prepare the grammar in such a way as to
fit into this parameter list, and hence addressing that must come next.

[Coding the Lexer - Revisited](#___top "click to go to top of document"){#Coding_the_Lexer_-_Revisited .u}
==========================================================================================================

The coder thus needs to develop regexps etc which can be fed directly
into the chosen DFA, here
[Set::FA::Element](http://metacpan.org/module/Set::FA::Element){.podlinkpod},
or which can be transformed somehow into a format acceptable to that
module. But so far I haven\'t actually said how I do that. It\'s time to
be explicit\....

I use a spreadsheet with 9 columns:

[o Start]{#o_Start}

:   This just contains 1 word, \'Yes\', against the name of the state
    which is the start state.

[o Accept]{#o_Accept}

:   This contains the word \'Yes\' against the name of any state which
    will be an accepting state (see above).

[o State]{#o_State}

:   This is the name of the state.

[o Event]{#o_Event}

:   This is a regexp, which is read to mean: The event fires (is
    triggered) if the current input char matches the regexp in this
    column.

    Now, since the regexp belongs to a given state, we know the DFA will
    only process regexps associated with the current state, of which
    there will be 1 or at most a few.

    When there are multiple regexps per state, I leave all other columns
    empty.

[o Next]{#o_Next}

:   The name of the \'next\' state, i.e. the name of the state to which
    the STT will jump if the current char matches the regexp given on
    the same line of the spreadsheet (in the current state of course).

[o Entry]{#o_Entry}

:   The optional name of the function the DFA is to call upon (just
    before) entry to the (new) state.

[o Exit]{#o_Exit}

:   The optional name of the function the DFA is to call upon exiting
    from the current state.

[o Regexp]{#o_Regexp}

:   This is a working column, in which I put formulas so that I can
    refer to them in various places in the \'Event\' column. It is not
    passed to the DFA in the \'transitions\' parameter.

[o Interpretation]{#o_Interpretation}

:   Comments to self.

The STT for
[GraphViz2::Marpa](http://metacpan.org/module/GraphViz2::Marpa){.podlinkpod}
is [on-line
here](http://savage.net.au/Perl-modules/html/graphviz2.marpa/stt.html){.podlinkurl}.

Now, this structure has various advantages:

[o Legibility]{#o_Legibility}

:   It is very easy to read, and to work with. Don\'t forget, to start
    with you\'ll be basically switching back and forth between the
    grammar definition document (hopefully in BNF) and this spreadsheet.
    This is a way of saying there\'s no coding done at this stage.

[o Exportability]{#o_Exportability}

:   Since I have not yet addressed the question of how the code will
    read the spreadsheet, I offer these techniques:

    [o Read the spreadsheet directly]{#o_Read_the_spreadsheet_directly}

    :   There is no problem with this method, except the complexity of
        the code (in the external module which does the reading of
        course), and the slowness of loading and running this code.

        Actually, I should mention that since I use
        [LibreOffice](http://www.libreoffice.org/){.podlinkurl} I can
        either force end-users to install
        [OpenOffice::OODoc](http://metacpan.org/module/OpenOffice::OODoc){.podlinkpod},
        or export the spreadsheet as an Excel file, in order to avail
        themselves of this option. I have chosen to not support reading
        the \*.ods file directly in the modules
        ([Graph::Easy::Marpa](http://metacpan.org/module/Graph::Easy::Marpa){.podlinkpod}
        and
        [GraphViz2::Marpa](http://metacpan.org/module/GraphViz2::Marpa){.podlinkpod})
        I ship.

    [o Export the spreadsheet to a CSV file first]{#o_Export_the_spreadsheet_to_a_CSV_file_first}

    :   This way, we can read a CSV file into the DFA fairly quickly,
        without loading the module which reads spreadsheets.

        Be careful here with LibreOffice, since it forces you to use
        Unicode for the spreadsheet, but exports e.g. double-quotes as
        the 3 byte sequence 0xe2, 0x80, 0x9c, which when used in a
        regexp will never match a \'real\' double-quote in your input
        stream. Sigh. Do No Evil. If only. So, when exporting, *always*
        choose the ASCII option.

    [o Incorporate the spreadsheet directly into our code (my favourite)]{#o_Incorporate_the_spreadsheet_directly_into_our_code_(my_favourite)}

    :   We do this in 2 stages: Export to a CSV file, and just use an
        editor to append that file to the end of the source code of our
        module, after the \_\_DATA\_\_ token.

        Such in-line data can be accessed effortlessly by the very neat
        and very fast module
        [Data::Section::Simple](http://metacpan.org/module/Data::Section::Simple){.podlinkpod}.
        Clearly, since our module has been loaded already, because it\'s
        precisely what\'s being executed, there is essentially no
        overhead whatsoever in reading data from within it. Don\'t you
        just love Perl! And MetaCPAN of course. And a community which
        contributes such wonderous code.

        An advantage of this alternative is that it lets end-users edit
        the shipped \*.csv or \*.ods files, after which they can use a
        command line option on scripts to read their file, over-riding
        the built-in STT.

After all this, it\'s just a matter of code which read and validates the
structure of the STT\'s data, and then reformats it into what
[Set::FA::Element](http://metacpan.org/module/Set::FA::Element){.podlinkpod}
demands.

So, enough about the lexer, but we can say that by now the first
sub-grammar has been incorporated into the design and code of the lexer,
and that the second sub-grammar must now be encoded into the parser, for
that\'s how the parser performs syntax checking.

[Coding the Parser](#___top "click to go to top of document"){#Coding_the_Parser .u}
====================================================================================

How we do this depends intimately on which pre-existing module, if any,
we choose to use to aid the development of the parser. Since I choose
Marpa (currently
[Marpa::R2](http://metacpan.org/module/Marpa::R2){.podlinkpod}), I am
orienting this article to that module. However, only in the next article
will I deal in depth with Marpa.

Whichever module is chosen, you can think of the process like this: Our
input stream is a set of pre-defined tokens (probably but not
necessarily output from the lexer), and we must now specify all possible
legal combinations of those tokens, i.e. the syntax of the language.
This really means *the remainder* of the syntax, since by now we\'ve
lost interest in the definition of a (legal) token. I.e. at this point
we are assuming all incoming tokens are legal, which is a way of saying
we will not try to parse and run a program containing token-based syntax
errors, although it may contain logic errors (even if written in Perl
:-).

Then, a combination of tokens which does not match any of the given
legal combinations can be immediately rejected as a syntax error. And
keep in mind that the friendliest compilers find as many syntax errors
as possible per parse.

And since this check takes place on a token-by-token basis, we (ought
to) know precisely which token triggered the error, which means we can
emit a nice error message, identifying the culprit and its context.

[Sample Parser Code](#___top "click to go to top of document"){#Sample_Parser_Code .u}
======================================================================================

Here\'s a sample of a Marpa::R2 grammar (adapted from its synopsis):

            my($grammar) = Marpa::R2::Grammar -> new
            ({
                    actions => 'My_Actions',
                    start   => 'Expression',
                    rules   =>
                    [
                            { lhs => 'Expression', rhs => [qw/Term/] },
                            { lhs => 'Term',       rhs => [qw/Factor/] },
                            { lhs => 'Factor',     rhs => [qw/Number/] },
                            { lhs => 'Term',       rhs => [qw/Term Add Term/],
                                    action => 'do_add'
                            },
                            { lhs => 'Factor',     rhs => [qw/Factor Multiply Factor/],
                                    action => 'do_multiply'
                            },
                    ],
                    default_action => 'do_something',
            });

We need to understand these parameters before being able to write
something like this for our chosen grammar.

Now, despite the differences between this and the calls to
Set::FA::Element -\> new() above, it\'s basically the same:

[o actions]{#o_actions}

:   This is the name of a Perl package in which actions such as
    do\_add() and do\_multiply() will be looked for. OK, so the lexer
    has no such option, the \'current\' package being the default.

[o start]{#o_start}

:   This is the *lhs* name of the rule to start with, as with the lexer.

[o rules]{#o_rules}

:   This is just an arrayref of *rule descriptors* defining the syntax
    of the grammar. This is the lexer\'s *transitions* parameter.

[o default\_action]{#o_default_action}

:   Use this (optional) callback as the action for any rule element
    which does not explicitly specify its own action.

So our real problem is re-casting the syntax from BNF, or whatever, into
a set of these (lhs, rhs, action) *rule descriptors*.

Now, how do we think about such a problem. I suggest
contrast-and-compare real code with what the grammar says it must be:

Firstly, let\'s repeat *teamwork.dot* from above:

            digraph Perl
            {
            graph [ rankdir="LR" ]
            node  [ fontsize="12pt" shape="rectangle" style="filled, solid" ]
            edge  [ color="grey" ]
            "Teamwork" [ fillcolor="yellow" ]
            "Victory"  [ fillcolor="red" ]
            "Teamwork" -> "Victory" [ label="is the key to" ]
            }

Generalizing, we know a
[Graphviz](http://www.graphviz.org/){.podlinkurl} (DOT) graph must start
like one of these:

            strict digraph $id {...} # Case 1. $id is a variable.
            strict digraph     {...}
            strict   graph $id {...} # Case 3
            strict   graph     {...}
                   digraph $id {...} # Case 5
                   digraph     {...}
                     graph $id {...} # Case 7
                     graph     {...}

As indeed the real code does, with the graph\'s id being *Perl* (i.e.
case 5 in that list).

If you\'ve ever noticed that BNFs can be written as a tree (can they?),
you\'ll know what comes next: We\'re going to start writing *rule
descriptors* from the root down.

Drawing this as a tree gives:

                 DOT's Grammar
                      |
                      V
            ---------------------
            |                   |
         strict                 |
            |                   |
            ---------------------
                      |
                      V
            ---------------------
            |                   |
         digraph     or       graph
            |                   |
            ---------------------
                      |
                      V
            ---------------------
            |                   |
           $id                  |
            |                   |
            ---------------------
                      |
                      V
                    {...}

[Connecting the Parser back to the Lexer](#___top "click to go to top of document"){#Connecting_the_Parser_back_to_the_Lexer .u}
================================================================================================================================

But wait, what\'s this? I\'ve just said in that tree that the *strict*
is optional. Well, no it\'s not, in the parser. It is optional in the
DOT language, but I designed the lexer, and I therein ensured it would
necessarily output *strict =\> no* when the author of the graph omitted
the *strict*.

So, by the time we\'re inside the parser, it\'s no longer optional, and
that was done simply to make the life easier for consumers of the
lexer\'s output stream, such as authors of parsers.

Likewise, for *digraph* \'v\' *graph*, I designed the lexer to output
*digraph =\> \'yes\'* in one case and *digraph =\> \'no\'* in the other.

What does that mean? It means, for *teamwork.dot*, the lexer will output
(in some convenient format) the equivalent of:

            strict   => no
            digraph  => yes
            graph_id => Perl
            ...

*graph\_id* was chosen because the DOT language allows other types of
ids, e.g. for nodes, edges, ports and compass points.

This gives us our first 6 Marpa-friendly rules, embedded in an arrayref
of rules:

            [
            {   # Root-level stuff.
                    lhs => 'graph_grammar',
                    rhs => [qw/prolog_and_graph/],
            },
            {
                    lhs => 'prolog_and_graph',
                    rhs => [qw/prolog_definition graph_sequence_definition/],
            },
            {   # Prolog stuff.
                    lhs => 'prolog_definition',
                    rhs => [qw/strict_definition digraph_definition graph_id_definition/],
            },
            {
                    lhs    => 'strict_definition',
                    rhs    => [qw/strict/],
                    action => 'strict', # <== Callback.
            },
            {
                    lhs    => 'digraph_definition',
                    rhs    => [qw/digraph/],
                    action => 'digraph', # <== Callback.
            },
            {
                    lhs    => 'graph_id_definition',
                    rhs    => [qw/graph_id/],
                    action => 'graph_id', # <== Callback.
            },
            ...
            ]

That is, we\'re saying the graph, as a whole, consists of:

[o A prolog thingy]{#o_A_prolog_thingy}

And then\...

[o A graph sequence thingy]{#o_A_graph_sequence_thingy}

Remember, those names \'prolog\_and\_graph\' etc are just ids I made up.

Next, a prolog consists of:

[o A strict thingy]{#o_A_strict_thingy}

:   Which is now not optional, and then\...

[o A digraph thingy]{#o_A_digraph_thingy}

:   Which will turn out to match the lexer input of /\^(di\|)graph\$/,
    and the lexer output of digraph =\> /\^(yes\|no)\$/, and then\...

[o A graph\_id]{#o_A_graph_id}

:   Which is optional, and then\...

[o Some other stuff]{#o_Some_other_stuff}

:   Which will be the precise definition of real live graphs,
    represented above by {\...} in the list of the 8 possible formats
    for the prolog.

[Something Fascinating about Rule Descriptors](#___top "click to go to top of document"){#Something_Fascinating_about_Rule_Descriptors .u}
==========================================================================================================================================

But take another look at those rule descriptors. They say *nothing*
about the values of the tokens! For instance, in *graph\_id =\> Perl*
what happens to ids such as *Perl*. Nothing. They are ignored. And
that\'s because that\'s just how these grammars work.

Recall: It was the *lexer*\'s job to identify valid graph ids based on
the 1st sub-grammar. By the time the data hits the parser, we know we
have a valid graph id, and as long as it plugs in to the *structure* of
the grammar in the right place, we are prepared to accept *any valid*
graph id. Hence
[Marpa::R2](http://metacpan.org/module/Marpa::R2){.podlinkpod} does not
even look at the graph id, which is a way of saying this one grammar
works with every valid graph id.

This point also raises the tricky discussion of whether a specific
implementation of lexer/parser code can or must keep the 2 phases
separate, or whether in fact you can roll them into one without falling
for the \'premature optimisation\' trap. I\'ll just draw a veil over
that discussion, since I\'ve already declared my stance: They\'re
implemented in 2 modules.

[Chains and Trees](#___top "click to go to top of document"){#Chains_and_Trees .u}
==================================================================================

But if these rules have to be chained into a tree, how do we handle the
root? Well, consider this call to
[Marpa::R2](http://metacpan.org/module/Marpa::R2){.podlinkpod}\'s new()
method:

            my($grammar) = Marpa::R2::Grammar -> new(... start => 'graph_grammar', ...);

And *graph\_grammar* is precisely the *lhs* in the first rule
descriptor.

After that, every rule\'s *rhs*, including the root\'s, must be defined
later in the list of rule descriptors. This forms the links in the
chain, and if drawn you\'ll see the end result is a tree.

Here\'s the full
[Marpa::R2](http://metacpan.org/module/Marpa::R2){.podlinkpod} grammar
for DOT (as used in the
[GraphViz2::Marpa](http://metacpan.org/module/GraphViz2::Marpa){.podlinkpod}
module) as an image:
<http://savage.net.au/Ron/html/graphviz2.marpa/Marpa.Grammar.svg>. This
image was created with (you guessed it!)
[Graphviz](http://www.graphviz.org/){.podlinkurl} via
[GraphViz2](http://metacpan.org/module/GraphViz2){.podlinkpod}. Numbers
have been added to node names in the tree, otherwise Graphviz would
regard any 2 identical numberless names as one and the same node.

[Less Coding - More Design](#___top "click to go to top of document"){#Less_Coding_-_More_Design .u}
====================================================================================================

Here I\'ll stop building the tree of the grammar (see the next article),
and turn to some design issues.

[My Rules-of-Thumb for Writing Lexers/Parsers](#___top "click to go to top of document"){#My_Rules-of-Thumb_for_Writing_Lexers/Parsers .u}
==========================================================================================================================================

The remainder of this document is to help beginners orient their
thinking when confronted with a problem they don\'t have experience at
tackling. Of course, if you\'re an expert in lexing and parsing, feel
free to ignore everything I say.

And, if you think I\'ve misused lexing/parsing terminology here, please
let me know.

[Eschew Premature Optimisation](#___top "click to go to top of document"){#Eschew_Premature_Optimisation .u}
------------------------------------------------------------------------------------------------------------

Yep, this old one again. It has various connotations:

[o The lexer and the parser]{#o_The_lexer_and_the_parser}

:   Don\'t aim to combine the lexer and parser, even though that\'s what
    might eventuate.

    I.e. wait until the design of each is clear and finalized, before
    trying to jam them into a single module (or program).

[o The lexer and the tokens]{#o_The_lexer_and_the_tokens}

:   Do make the lexer identify the existence of tokens, but not identify
    their ultimate role or meaning.

[o The lexer and context]{#o_The_lexer_and_context}

:   Don\'t make the lexer do context analysis.

    Here I mean make the parser be the one to disambiguate tokens with
    multiple meanings, by using the context, which at this point are
    tokens identified by the lexer.

    And [context analysis for
    businesses](http://en.wikipedia.org/wiki/Context_analysis){.podlinkurl},
    for example, is probably not what you want either.

[o The lexer and syntax]{#o_The_lexer_and_syntax}

:   Don\'t make the lexer do syntax checking. This is effectively the
    same as the last point.

[o The lexer and its output]{#o_The_lexer_and_its_output}

:   Don\'t minimize the lexer\'s output stream. For instance, don\'t
    force the code which reads the lexer\'s output to guess whether or
    not a variable-length set of tokens has ended. Output a specific
    token as a set terminator. The point of this token is to tell the
    parser exactly what\'s going on. Without such a token, the next
    token has to do double-duty: Firstly it tells the parser the
    variable-length part has finished, and secondly, it represents
    itself. Such overloading is unnecessary.

[o The State Transition Table]{#o_The_State_Transition_Table}

:   In the STT, don\'t try to minimize the number of states, at least
    not until the code has stabilized (i.e. is no longer under \[rapid\]
    development).

    I develop my STTs in a spreadsheet, which means a formula (regexp)
    stored in 1 cell can be referenced in any number of other cells.
    This is *very* convenient.

[Divide and Conquer](#___top "click to go to top of document"){#Divide_and_Conquer .u}
--------------------------------------------------------------------------------------

Hmmm, another ancient
[aphorism](http://en.wikipedia.org/wiki/Aphorism){.podlinkurl}.
Naturally, these persist precisely because they\'re telling us something
important.

Here, it means study the problem carefully, and deal with each part
(lexer, parser) of it separately. \'Nuff said.

[Don\'t Reinvent the Wheel](#___top "click to go to top of document"){#Don't_Reinvent_the_Wheel .u}
---------------------------------------------------------------------------------------------------

Yes, I know *you\'d* never do that.

Anyway, there are Perl modules to help with things like the STT. E.g.:
[Set::FA::Element](http://metacpan.org/module/Set::FA::Element){.podlinkpod}.
Check its \'See Also\' (in
[Set::FA](http://metacpan.org/module/Set::FA){.podlinkpod}, actually)
for other STT helpers.

[Be Patient with the STT](#___top "click to go to top of document"){#Be_Patient_with_the_STT .u}
------------------------------------------------------------------------------------------------

Developing the STT takes many iterations:

[o The test cases]{#o_The_test_cases}

:   For each iteration, prepare a separate test case.

[o The tiny script]{#o_The_tiny_script}

:   Have a tiny script which runs 1 test. Giving it a short, perhaps
    temporary, name, makes each test just that little bit easier to run.

    By temporary name I mean you can give it a meaningful name later,
    when including it in the distro.

[o The wrapper script]{#o_The_wrapper_script}

:   Have a script which runs all tests.

    I keep the test data files in the data/ dir, and the scripts in the
    scripts/ dir. Then, creating tests in the t/ dir can perhaps utilize
    these two sets of helpers.

    Since I\'ve only used
    [Marpa::R2](http://metacpan.org/module/Marpa::R2){.podlinkpod} for
    graphical work, the output of the wrapper is a web page, which makes
    viewing the results simple. I like to include (short) input or
    output text files on such a page, beside the \*.svg images. That way
    I can see at a glance what the input was and hence I can tell what
    the output should be without switching to the editor\'s window.

    There\'s a little bit of effort initially, but after that it\'s *so*
    easy to check the output of the latest test.

Sample output from my wrapper scripts:

[GraphViz2
(non-Marpa)](http://savage.net.au/Perl-modules/html/graphviz2/){.podlinkurl}

[GraphViz2::Marpa](http://savage.net.au/Perl-modules/html/graphviz2.marpa/){.podlinkurl}

[GraphViz2::Marpa::PathUtils](http://savage.net.au/Perl-modules/html/graphviz2.pathutils/){.podlinkurl}

[Graph::Easy::Marpa](http://savage.net.au/Perl-modules/html/graph.easy.marpa/){.podlinkurl}

[Be Patient with the Grammar](#___top "click to go to top of document"){#Be_Patient_with_the_Grammar .u}
--------------------------------------------------------------------------------------------------------

As with the STT, this, at least for me, is very much a trial-and-error
process.

Tips:

[o Paper, not code]{#o_Paper,_not_code}

:   A good idea is not to start by coding with your editor, but to draw
    the grammar as a tree, on paper.

[o Watch out for alternatives]{#o_Watch_out_for_alternatives}

:   This refers to when one of several tokens can appear in the input
    stream. Learn exactly how to draw that without trying to minimize
    (see above) the number of branches in the tree.

    Of course, you will still need to learn how to code such a
    construct. Here\'s a bit of code from
    [Graph::Easy::Marpa](http://metacpan.org/module/Graph::Easy::Marpa){.podlinkpod}
    which deals with this (note: we\'re back to the Graph::Easy language
    from here on!):

                {   # Graph stuff.
                        lhs => 'graph_definition',
                        rhs => [qw/graph_statement/],
                },
                {
                        lhs => 'graph_statement', # 1 of 3.
                        rhs => [qw/group_definition/],
                },
                {
                        lhs => 'graph_statement', # 2 of 3.
                        rhs => [qw/node_definition/],
                },
                {
                        lhs => 'graph_statement', # 3 of 3.
                        rhs => [qw/edge_definition/],
                },

    This is telling you that a graph thingy can be any one of a group,
    node or edge. It\'s
    [Marpa::R2](http://metacpan.org/module/Marpa::R2){.podlinkpod}\'s
    job to try the 1/2/3 of 3 in order, to see which (if any) matches
    the input stream.

    So, this represents a point in the input stream where one of several
    *alternatives* can appear.

    The tree would look like:

                                graph_definition
                                       |
                                       V
                                graph_statement
                                       |
                                       V
                    ---------------------------------------
                    |                  |                  |
                    V                  V                  V
             group_definition   node_definition    edge_definition

    The comment \'3 of 3\', for instance, says an edge can stand alone.

[o Watch out for sequences]{#o_Watch_out_for_sequences}

:   But consider the *node\_definition*:

                {   # Node stuff.
                        lhs => 'node_definition',
                        rhs => [qw/node_sequence/],
                        min => 0,
                },
                {
                        lhs => 'node_sequence', # 1 of 4.
                        rhs => [qw/node_statement/],
                },
                {
                        lhs => 'node_sequence', # 2 of 4.
                        rhs => [qw/node_statement daisy_chain_node/],
                },
                {
                        lhs => 'node_sequence', # 3 of 4.
                        rhs => [qw/node_statement edge_definition/],
                },
                {
                        lhs => 'node_sequence', # 4 of 4.
                        rhs => [qw/node_statement group_definition/],
                },

    Here the comment \'3 of 4\' tells you that nodes can be followed by
    edges.

    A realistic sample is: \[node\_1\] -\> \[node\_2\], where \'\[x\]\'
    is a node and \'-\>\' is an edge, because an edge can be followed by
    a node (applying \'3 of 4\' below).

    So, this (above and below) represents a point in the input stream
    where one of several specific *sequences* of tokens are
    allowed/expected. Here\'s the *edge\_definition*:

                {   # Edge stuff.
                        lhs => 'edge_definition',
                        rhs => [qw/edge_sequence/],
                        min => 0,
                },
                {
                        lhs => 'edge_sequence', # 1 of 4.
                        rhs => [qw/edge_statement/],
                },
                {
                        lhs => 'edge_sequence', # 2 of 4.
                        rhs => [qw/edge_statement daisy_chain_edge/],
                },
                {
                        lhs => 'edge_sequence', # 3 of 4.
                        rhs => [qw/edge_statement node_definition/],
                },
                {
                        lhs => 'edge_sequence', # 4 of 4.
                        rhs => [qw/edge_statement group_definition/],
                },
                {
                        lhs => 'edge_statement',
                        rhs => [qw/edge_name attribute_definition/],
                },
                {
                        lhs    => 'edge_name',
                        rhs    => [qw/edge_id/],
                        action => 'edge_id',
                },

But, I have to stop somewhere, so\...

[Wrapping Up and Winding Down](#___top "click to go to top of document"){#Wrapping_Up_and_Winding_Down .u}
==========================================================================================================

I hope I\'ve clarified what can be a complex and daunting part of
programming, and I also hope I\'ve convinced you that working in Perl,
with the help of a spreadsheet, is the modern aka only way to lexer and
parser bliss.

[Author](#___top "click to go to top of document"){#Author .u}
==============================================================

Ron Savage
![](http://savage.net.au/assets/images/local/email-address.png).

Home page: <http://savage.net.au/index.html>

[Licence](#___top "click to go to top of document"){#Licence .u}
================================================================

Australian Copyright © 2012 Ron Savage. All rights reserved.

            All Programs of mine are 'OSI Certified Open Source Software';
            you can redistribute them and/or modify them under the terms of
            The Artistic License, a copy of which is available at:
            http://www.opensource.org/licenses/index.html
