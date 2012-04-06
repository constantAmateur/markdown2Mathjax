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
