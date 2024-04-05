import re, sys, types, copy, os

__version__ = "2.5"
__tabversion__ = "2.4"       

_is_identifier = re.compile(r'^[a-zA-Z0-9_]+$')

try:
    _INSTANCETYPE = (types.InstanceType, types.ObjectType)
except AttributeError:
    _INSTANCETYPE = types.InstanceType
    class object: pass      

class LexError(Exception):
    def __init__(self, message, s):
         self.args = (message,)
         self.text = s

class LexWarning(object):
   def __init__(self):
      self.warned = 0
   def __call__(self, msg):
      if not self.warned:
         sys.stderr.write("ply.lex: Warning: " + msg+"\n")
         self.warned = 1

_SkipWarning = LexWarning()         

class LexToken(object):
    def __str__(self):
        return "LexToken(%s,%r,%d,%d)" % (self.type,self.value,self.lineno,self.lexpos)
    def __repr__(self):
        return str(self)
    def skip(self, n):
        self.lexer.skip(n)
        _SkipWarning("Calling t.skip() on a token is deprecated.  Please use t.lexer.skip()")

class Lexer:
    def __init__(self):
        self.lexre = None             # Master regular expression. This is a list of
                                      # tuples (re,findex) where re is a compiled
                                      # regular expression and findex is a list
                                      # mapping regex group numbers to rules
        self.lexretext = None         # Current regular expression strings
        self.lexstatere = {}          # Dictionary mapping lexer states to master regexs
        self.lexstateretext = {}      # Dictionary mapping lexer states to regex strings
        self.lexstaterenames = {}     # Dictionary mapping lexer states to symbol names
        self.lexstate = "INITIAL"     # Current lexer state
        self.lexstatestack = []       # Stack of lexer states
        self.lexstateinfo = None      # State information
        self.lexstateignore = {}      # Dictionary of ignored characters for each state
        self.lexstateerrorf = {}      # Dictionary of error functions for each state
        self.lexreflags = 0           # Optional re compile flags
        self.lexdata = None           # Actual input data (as a string)
        self.lexpos = 0               # Current position in input text
        self.lexlen = 0               # Length of the input text
        self.lexerrorf = None         # Error rule (if any)
        self.lextokens = None         # List of valid tokens
        self.lexignore = ""           # Ignored characters
        self.lexliterals = ""         # Literal characters that can be passed through
        self.lexmodule = None         # Module
        self.lineno = 1               # Current line number
        self.lexdebug = 0             # Debugging mode
        self.lexoptimize = 0          # Optimized mode

    def clone(self, object=None):
        c = copy.copy(self)
        if object:
            newtab = { }
            for key, ritem in self.lexstatere.items():
                newre = []
                for cre, findex in ritem:
                     newfindex = []
                     for f in findex:
                         if not f or not f[0]:
                             newfindex.append(f)
                             continue
                         newfindex.append((getattr(object, f[0].__name__), f[1]))
                newre.append((cre, newfindex))
                newtab[key] = newre
            c.lexstatere = newtab
            c.lexstateerrorf = { }
            for key, ef in self.lexstateerrorf.items():
                c.lexstateerrorf[key] = getattr(object, ef.__name__)
            c.lexmodule = object
        return c

    def writetab(self, tabfile, outputdir=""):
        if isinstance(tabfile, types.ModuleType):
            return
        basetabfilename = tabfile.split(".")[-1]
        filename = os.path.join(outputdir, basetabfilename) + ".py"
        tf = open(filename, "w")
        tf.write("# %s.py. This file automatically created by PLY (version %s). Don't edit!\n" % (tabfile, __version__))
        tf.write("_lextokens    = %s\n" % repr(self.lextokens))
        tf.write("_lexliterals  = %s\n" % repr(self.lexliterals))
        tf.write("_lexreflags   = %d\n" % self.lexreflags)
        tf.write("_lexignore    = %s\n" % repr(self.lexignore))
        tf.write("_lexerrorf    = %s\n" % repr(self.lexerrorf and self.lexerrorf.__name__ or None))
        tf.write("_lexstateinfo = %s\n" % repr(self.lexstateinfo))
        tf.write("_lexstatere   = {\n")
        for key, ritem in self.lexstatere.items():
            tf.write("  %s : [\n" % repr(key))
            for cre, findex in ritem:
                tf.write("     (re.compile(%s, %d), [\n" % (repr(cre.pattern), cre.flags))
                for f in findex:
                    if not f or not f[0]:
                        tf.write("       None,\n")
                        continue
                    tf.write("       (%s, %s),\n" % (f[0].__name__, f[1]))
                tf.write("     ]),\n")
            tf.write("  ],\n")
        tf.write("}\n")
        tf.write("_lexstateerrorf = {\n")
        for key, ef in self.lexstateerrorf.items():
            tf.write("  %s : %s,\n" % (repr(key), ef.__name__))
        tf.write("}\n")
        tf.close()

    def readtab(self, tabfile):
        if isinstance(tabfile, types.ModuleType):
            return
        m = __import__(tabfile)
        if not hasattr(m, "_lextokens"):
            raise ImportError("No _lextokens in %s" % tabfile)
        if not hasattr(m, "_lexstatere"):
            raise ImportError("No _lexstatere in %s" % tabfile)
        if not hasattr(m, "_lexstateerrorf"):
            raise ImportError("No _lexstateerrorf in %s" % tabfile)
        self.lextokens    = m._lextokens
        self.lexliterals  = m._lexliterals
        self.lexreflags   = m._lexreflags
        self.lexignore    = m._lexignore
        self.lexerrorf    = m._lexerrorf
        self.lexstateinfo = m._lexstateinfo
        self.lexstatere   = { }
        for key, ritem in m._lexstatere.items():
            newre = []
            for cre, findex in ritem:
                newfindex = []
                for f in findex:
                    newfindex.append((getattr(self, f[0]), f[1]))
                newre.append((re.compile(cre[0], cre[1]), newfindex))
            self.lexstatere[key] = newre
        self.lexstateerrorf = { }
        for key, ef in m._lexstateerrorf.items():
            self.lexstateerrorf[key] = getattr(self, ef)
        return 1

    def error(self, t):
        raise SyntaxError("Illegal character '%s' at line %d" % (t.value[0], t.lineno))

    def enable(self, type):
        if type not in self.lexstatere:
            raise ValueError("Undefined state '%s'" % type)
        self.lexstateinfo[type] = 1

    def disable(self, type):
        if type not in self.lexstatere:
            raise ValueError("Undefined state '%s'" % type)
        self.lexstateinfo[type] = 0

    def push_state(self, type):
        self.lexstatestack.append(self.lexstate)
        self.lexstate = type

    def pop_state(self):
        self.lexstate = self.lexstatestack.pop()

    def _compile_master(self):

        lexre = []

        literals = {}
        lits = self.lexliterals.split("'")
        for i in range(0,len(lits),2):
            literals[lits[i]] = 1

        if self.lexre:
            self.lexretext = []
            for reg in self.lexre:
                if isinstance(reg, str):
                    self.lexretext.append(reg)
                    continue
                lexre.append(reg)

        max = 0
        for lexre_s, lexindex in lexre:
            for lex, index in lexindex:
                if not lex:
                    continue
                if len(lex) > max:
                    max = len(lex)
        if max == 0:
            return
        for i in range(max, 0, -1):
            lre = []
            for lexre_s, lexindex in lexre:
                indexlist = []
                for lex, index in lexindex:
                    if not lex:
                        indexlist.append((None, index))
                        continue
                    if len(lex) < i:
                        continue
                    re_text = "(%s)" % lex[0:i]
                    indexlist.append((re.compile(re_text, self.lexreflags), index))
                lre.append((lexre_s, indexlist))
            if not lre:
                continue
            lexre.append((lre, max-i))
        self.lexre = []
        self.lexretext = []
        for lexre_s, lexindex in lexre:
            self.lexretext.append(lexre_s)
            self.lexre.append(lexindex)

    def input(self, s):
        self.lexdata = s
        self.lexpos = 0
        self.lexlen = len(s)

    def token(self):
        if not self.lexdata:
            return None
        if not self.lexreflags & re.UNICODE:
            lexpos = self.lexpos
            m = None
            while True:
                for lexre, lexindex in self.lexstatere[self.lexstate]:
                    for lex, index in lexindex:
                        if not lex:
                            continue
                        m = lexre.match(self.lexdata, lexpos)
                        if not m:
                            continue
                        i = m.lastindex
                        j = m.end(i)
                        tok = LexToken()
                        tok.value = m.group(i)
                        tok.lineno = self.lineno
                        tok.lexpos = lexpos
                        tok.type = self.lextokens[index]
                        tok.lexpos = lexpos
                        if tok.type == 'error':
                            self.lexerrorf(tok)
                            break
                        self.lexpos = j
                        if tok.type == 'ignore':
                            break
                        return tok
                    if m:
                        break
                else:
                    if self.lexdata[lexpos] == '\n':
                        self.lineno += 1
                    if self.lexignore:
                        while self.lexdata[lexpos] in self.lexignore:
                            lexpos += 1
                            if lexpos >= self.lexlen:
                                return None
                    else:
                        lexpos += 1
                        if lexpos >= self.lexlen:
                            return None
                    if self.lexerrorf:
                        tok = LexToken()
                        tok.value = self.lexdata[self.lexpos]
                        tok.lineno = self.lineno
                        tok.lexpos = lexpos
                        tok.type = 'error'
                        self.lexerrorf(tok)
                        self.lexpos += 1
                        continue
                    else:
                        self.error(tok)
                lexpos += 1
                if lexpos >= self.lexlen:
                    return None
        else:
            lexpos = self.lexpos
            while True:
                for lexre, lexindex in self.lexstatere[self.lexstate]:
                    for lex, index in lexindex:
                        if not lex:
                            continue
                        m = lexre.match(self.lexdata, lexpos)
                        if not m:
                            continue
                        i = m.lastindex
                        j = m.end(i)
                        tok = LexToken()
                        tok.value = m.group(i)
                        tok.lineno = self.lineno
                        tok.lexpos = lexpos
                        tok.type = self.lextokens[index]
                        tok.lexpos = lexpos
                        if tok.type == 'error':
                            self.lexerrorf(tok)
                            break
                        self.lexpos = j
                        if tok.type == 'ignore':
                            break
                        return tok
                    if m:
                        break
                else:
                    if self.lexdata[lexpos] == '\n':
                        self.lineno += 1
                    if self.lexignore:
                        while self.lexdata[lexpos] in self.lexignore:
                            lexpos += 1
                            if lexpos >= self.lexlen:
                                return None
                    else:
                        lexpos += 1
                        if lexpos >= self.lexlen:
                            return None
                    if self.lexerrorf:
                        tok = LexToken()
                        tok.value = self.lexdata[self.lexpos]
                        tok.lineno = self.lineno
                        tok.lexpos = lexpos
                        tok.type = 'error'
                        self.lexerrorf(tok)
                        self.lexpos += 1
                        continue
                    else:
                        self.error(tok)
                lexpos += 1
                if lexpos >= self.lexlen:
                    return None

    def _main(self):
        while True:
            tok = self.token()
            if not tok:
                break
            if self.lexdebug:
                print("Token",tok)
