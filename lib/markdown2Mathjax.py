__version_info__ = (0,2,0)
__version__ = '.'.join(map(str,__version_info__))
__author__ = "Matthew Young"

import re

def break_tie(inline,equation):
    """If one of the delimiters is a substring of the other (e.g., $ and $$) it is possible that the two will begin at the same location.  In this case we need some criteria to break the tie and decide which operation takes precedence.  I've gone with the longer of the two delimiters takes priority (for example, $$ over $).  This function should return a 2 for the equation block taking precedence, a 1 for the inline block.  The magic looking return statement is to map 0->2 and 1->1."""
    tmp=(inline.end()-inline.start() > equation.end()-equation.start())
    return (tmp*3+2)%4


def sanitizeInput(string,inline_delims=["$","$"],equation_delims=["$$","$$"]):
    """Given a string that will be passed to markdown, the content of the different math blocks is stripped out and replaced by a 1 (for inline math) or a 2 (for equation mode).  The inline delimiters are used to surround the stripped out block in both cases.  A list of lists containing the stripped math code is also returned.  The sanitized string can then be passed safetly through markdown and then reconstructed with reconstructMath.

    There are potential four delimiters that can be specified.  The left and right delimiters for inline and equation mode math.  These can potentially be anything that isn't processed in some way by markdown and is compatible with mathjax (see documentation for both)."""
    placeholders=[inline_delims[0]+"1"+inline_delims[1],inline_delims[0]+"2"+inline_delims[1]]
    inline_left=re.compile("(?<!\\\\)"+re.escape(inline_delims[0]))
    inline_right=re.compile("(?<!\\\\)"+re.escape(inline_delims[1]))
    equation_left=re.compile("(?<!\\\\)"+re.escape(equation_delims[0]))
    equation_right=re.compile("(?<!\\\\)"+re.escape(equation_delims[1]))
    ilscanner=[inline_left.scanner(string),inline_right.scanner(string)]
    eqscanner=[equation_left.scanner(string),equation_right.scanner(string)]
    scanners=[ilscanner,eqscanner]
    
    #inBlack is 0 for not in a block, 1 for inline block, 2 for equation
    inBlock=0
    post=-1
    startpoints=[ilscanner[0].search(),eqscanner[0].search()]
    terminator=-1
    codeblocks=[[],[]]
    sanitizedString=''
    while 1:
        #find the next point of interest.
        while startpoints[0] and startpoints[0].start()<post:
            startpoints[0]=ilscanner[0].search()
        while startpoints[1] and startpoints[1].start()<post:
            startpoints[1]=eqscanner[0].search()
        #Found next start of a block, see which one is sooner...
        if startpoints[0] is None and startpoints[1] is None:
    	    #No more blocks, add in the rest of string and be done with it...
    	    sanitizedString = sanitizedString + string[post*(post>=0):]
    	    return (sanitizedString, codeblocks)
        elif startpoints[0] is None:
            inBlock=2
        elif startpoints[1] is None:
            inBlock=1
        else:
            inBlock = (startpoints[0].start()<startpoints[1].start()) + (startpoints[0].start()>startpoints[1].start())*2
            if not inBlock:
                inBlock = break_tie(startpoints[0],startpoints[1])
	#To avoid having to write this in all the places inBlock is used...
	inBlock=inBlock-1
        #Magic to ensure minimum index is 0
        sanitizedString = sanitizedString+string[(post*(post>=0)):startpoints[inBlock].start()]
        post = startpoints[inBlock].end()
        #Now find the matching end...
        while terminator<post:
            endpoint=scanners[inBlock][1].search()
            #If we run out of terminators before ending this loop, we're done
    	    if endpoint is None:
    	        #Add the unterminated codeblock to the sanitized string
    	        sanitizedString = sanitizedString + string[startpoints[inBlock].start():]
    	        return (sanitizedString, codeblocks)
    	    terminator=endpoint.start()
        #Add the bit to the appropriate codeblock...
        codeblocks[inBlock].append(string[post:endpoint.start()])
        #Now add in the appropriate placeholder
        sanitizedString = sanitizedString+placeholders[inBlock]
        #Fabulous.  Now we can start again once we update post...
        post = endpoint.end()

def reconstructMath(processedString,codeblocks,inline_delims=["$","$"],equation_delims=["$$","$$"],htmlSafe=False):
    """This is usually the output of sanitizeInput, after having passed the output string through markdown.  The delimiters given to this function should match those used to construct the string to begin with.

     This will output a string containing html suitable to use with mathjax.
     
     "<" and ">" "&" symbols in math can confuse the html interpreter because they mark the begining and end of definition blocks.  To avoid issues, if htmlSafe is set to True these symbols will be replaced by ascii codes in the math blocks. The downside to this is that if anyone is already doing this, there already niced text might be mangled (I think I've taken steps to make sure it won't but not extensively tested...)"""
    placeholders=[inline_delims[0]+"1"+inline_delims[1],inline_delims[0]+"2"+inline_delims[1]]
    #Make html substitutions.
    if htmlSafe:
        safeAmp=re.compile("&(?!(?:amp;|lt;|gt;))")
        for i in xrange(2):
            for j in xrange(len(codeblocks[i])):
	        codeblocks[i][j]=safeAmp.sub("&amp;",codeblock[i][j])
	        codeblocks[i][j]=codeblocks[i][j].replace("<","&lt;")
	        codeblocks[i][j]=codeblocks[i][j].replace(">","&gt;")
    #Sub the inline blocks back in to the sanitized string
    outString=processedString
    for i in xrange(len(codeblocks[0])):
        outString=outString.replace(placeholders[0],inline_delims[0]+codeblocks[0][i]+inline_delims[1],1)
    #Sub the equation blocks back in to the sanitized string
    for i in xrange(len(codeblocks[1])):
        outString=outString.replace(placeholders[1],equation_delims[0]+codeblocks[1][i]+equation_delims[1],1)
    return outString

def findBoundaries(string):
    """A depricated function.  Finds the location of string boundaries in a stupid way."""
    last=''
    twod=[]
    oned=[]
    boundary=False
    inoned=False
    intwod=False
    for count,char in enumerate(string):
        if char=="$" and last!='\\':
	    #We just hit a valid $ character!
            if inoned:
    	        oned.append(count)
    	        inoned=False
    	    elif intwod:
    	        if boundary:
    	            twod.append(count)
    	    	    intwod=False
    		    boundary=False
    	        else:
    	            boundary=True
    	    elif boundary:
	        #This means the last character was also a valid $
		twod.append(count)
		intwod=True
		boundary=False
    	    else:
	        #This means the last character was NOT a useable $
    	        boundary=True
        elif boundary:
	    #The last character was a valid $, but this one isn't...
	    #This means the last character was a valid $, but this isn't
	    if inoned:
	        print "THIS SHOULD NEVER HAPPEN!"
	    elif intwod:
	        #ignore it...
		pass
	    else:
	        oned.append(count-1)
		inoned=True
	    boundary=False
        last=char
    #What if we finished on a boundary character?  Actually doesn't matter, but let's include it for completeness
    if boundary:
        if not (inoned or intwod):
	    oned.append(count)
	    inoned=True
    return (oned,twod)
