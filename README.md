# nuventure

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0f7bbe0f12034ba998ce1a0d73ff72a3)](https://www.codacy.com/gh/waellison/nuventure/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=waellison/nuventure&amp;utm_campaign=Badge_Grade)

An interactive fiction engine written in Python.  I am currently in the
process of implementing this, and I will be documenting selected aspects
of the program's creation on my tech blog at some point; my blog is currently
under reconstruction.

Update the requirements (NLTK and numpy) by running `pip install -r
requirements.txt`.  This will install them if not present and update
them to the latest version if they are present.

Once `pip` has done its thing, you need to install an NLTK corpus (as
detailed on the [official NLTK site][0]):

```
zsh$ python
>>> import nltk
>>> nltk.download()
```

Given how small the input language for Nuventure is, it should suffice
to install any (English-language) corpus; I wrote and tested with the
`popular` package.

If you want to read the original design document for this program, you will
need a LaTeX compiler.  I use and suggest the [TeXLive][0] distribution
which is available for all modern platforms and comes with an editor, the
needed compilers, and output generation into PDF.  The built PDF is
available at <https://rt38.net/crap/nuventure-design.pdf>.

[0]: https://nltk.org
