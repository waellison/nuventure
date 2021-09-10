# nuventure

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7edeaead0a114735b54bd55d83a6ac86)](https://app.codacy.com/gh/tnwae/nuventure?utm_source=github.com&utm_medium=referral&utm_content=tnwae/nuventure&utm_campaign=Badge_Grade_Settings)

An interactive fiction engine written in Python.  I am currently in the process of implementing this, and I will be documenting selected aspects of the program's creation on my tech blog at <https://rt38.net/tag/nuventure>.

To run, you need NLTK: `pip install nltk`.  Once installed, you need to
install a corpus as described [on the NLTK site][0]:

```
# python
>>> import nltk
>>> nltk.download()
```

Given how small the input language for Nuventure is, it should suffice
to install any corpus; I wrote and tested with the `popular` package.
