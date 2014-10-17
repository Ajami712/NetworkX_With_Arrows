'''
Nassim's notes:
This code is mostly unchanged from its source.
All credit is due to the team at http://networkx.github.io/ who
certainly know more about coding than I do.

All major changes that I've made will be prefaced with
snippets of comments much like this one. All work was
done in Python 2.7.6.

I wrote this because I really wanted arrowheads in my network.
My changes to the function are a work in progress, but currently
here is what you can do:

- Have triangular arrows drawn along edges in your directed graph.

- Opt for traditional square boxes drawn along edges, in case you
want to differentiate between inhibition and activation.

- Modulate the width of the arrows and their position along the edge.
(This functionality has not been made into parameter inputs yet, but
they are currently present in the function as pre-set constants.)

I envision making those pre-set constants into actual parameters
sometime in the future. I am also interested in modifying the
actual edge-drawing functionality as well. At present, the
function does not seem capable of drawing loops (edges that start
and end at the same vertex). This seems fixable with some
shape manipulation via matplotlib.
'''

def draw_networkx_edges(G, pos,
                        edgelist=None,
                        width=1.0,
                        edge_color='k',
                        style='solid',
                        alpha=None,
                        edge_cmap=None,
                        edge_vmin=None,
                        edge_vmax=None,
                        ax=None,
                        arrows=True,
                        arrowheads=True,
                        apos_on_edge = 0.15,
                        label=None,
                        **kwds):
    """Draw the edges of the graph G.

    This draws only the edges of the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       Positions should be sequences of length 2.

    edgelist : collection of edge tuples
       Draw only specified edges(default=G.edges())

    width : float
       Line width of edges (default =1.0)

    edge_color : color string, or array of floats
       Edge color. Can be a single color format string (default='r'),
       or a sequence of colors with the same length as edgelist.
       If numeric values are specified they will be mapped to
       colors using the edge_cmap and edge_vmin,edge_vmax parameters.

    style : string
       Edge line style (default='solid') (solid|dashed|dotted,dashdot)

    alpha : float
       The edge transparency (default=1.0)

    edge_ cmap : Matplotlib colormap
       Colormap for mapping intensities of edges (default=None)

    edge_vmin,edge_vmax : floats
       Minimum and maximum for edge colormap scaling (default=None)

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    arrows : bool, optional (default=True)
       For directed graphs, if True draw arrowheads.

    arrowheads : bool, optional (default=True)
       For directed graphs, if True draw a traditional triangular arrowhead.
       If false, draw the old box-like structure instead.

    apos_on_edge : float, optional (default=0.15)
       For directed graphs, controls where the arrowhead appears
       along the edge. 0 is at the end of the edge, 1 is at the
       beginning of the edge.

    label : [None| string]
       Label for legend

    Returns
    -------
    matplotlib.collection.LineCollection
        `LineCollection` of the edges

    Notes
    -----
    For directed graphs, "arrows" (actually just thicker stubs) are drawn
    at the head end.  Arrows can be turned off with keyword arrows=False.
    Yes, it is ugly but drawing proper arrows with Matplotlib this
    way is tricky.

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> edges=nx.draw_networkx_edges(G,pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    http://networkx.lanl.gov/gallery.html

    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_labels()
    draw_networkx_edge_labels()
    """
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        import matplotlib.cbook as cb
        from matplotlib.colors import colorConverter, Colormap
        from matplotlib.collections import LineCollection
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()

    if edgelist is None:
        edgelist = G.edges()

    if not edgelist or len(edgelist) == 0:  # no edges!
        return None

    # set edge positions
    edge_pos = numpy.asarray([(pos[e[0]], pos[e[1]]) for e in edgelist])

    if not cb.iterable(width):
        lw = (width,)
    else:
        lw = width

    if not cb.is_string_like(edge_color) \
           and cb.iterable(edge_color) \
           and len(edge_color) == len(edge_pos):
        if numpy.alltrue([cb.is_string_like(c)
                         for c in edge_color]):
            # (should check ALL elements)
            # list of color letters such as ['k','r','k',...]
            edge_colors = tuple([colorConverter.to_rgba(c, alpha)
                                 for c in edge_color])
        elif numpy.alltrue([not cb.is_string_like(c)
                           for c in edge_color]):
            # If color specs are given as (rgb) or (rgba) tuples, we're OK
            if numpy.alltrue([cb.iterable(c) and len(c) in (3, 4)
                             for c in edge_color]):
                edge_colors = tuple(edge_color)
            else:
                # numbers (which are going to be mapped with a colormap)
                edge_colors = None
        else:
            raise ValueError('edge_color must consist of either color names or numbers')
    else:
        if cb.is_string_like(edge_color) or len(edge_color) == 1:
            edge_colors = (colorConverter.to_rgba(edge_color, alpha), )
        else:
            raise ValueError('edge_color must be a single color or list of exactly m colors where m is the number or edges')

    edge_collection = LineCollection(edge_pos,
                                     colors=edge_colors,
                                     linewidths=lw,
                                     antialiaseds=(1,),
                                     linestyle=style,
                                     transOffset = ax.transData,
                                     )



    edge_collection.set_zorder(1)  # edges go behind nodes
    edge_collection.set_label(label)
    ax.add_collection(edge_collection)

    # Note: there was a bug in mpl regarding the handling of alpha values for
    # each line in a LineCollection.  It was fixed in matplotlib in r7184 and
    # r7189 (June 6 2009).  We should then not set the alpha value globally,
    # since the user can instead provide per-edge alphas now.  Only set it
    # globally if provided as a scalar.
    if cb.is_numlike(alpha):
        edge_collection.set_alpha(alpha)

    if edge_colors is None:
        if edge_cmap is not None:
            assert(isinstance(edge_cmap, Colormap))
        edge_collection.set_array(numpy.asarray(edge_color))
        edge_collection.set_cmap(edge_cmap)
        if edge_vmin is not None or edge_vmax is not None:
            edge_collection.set_clim(edge_vmin, edge_vmax)
        else:
            edge_collection.autoscale()

    arrow_collection = None


    '''
    Nassim's notes:
    Everything in this function beyond this point has been heavily modified
    in order to incorporate arrows.
    '''

    if G.is_directed() and arrows:

        # a directed graph hack
        # draw thick line segments at head end of edge
        # waiting for someone else to implement arrows that will work
        arrow_colors = edge_colors
        a_pos = []

        '''
        Nassim's notes:
        We store the slopes of our edges' orthogonal lines as we go through the loop.
        Same goes for our angles theta and our edge lengths. We'll use these later.
        '''
        orthoslope = []
        thetas = []
        lengths = []
        p = 1.0-0.25  # make head segment 25 percent of edge length
        for src, dst in edge_pos:
            x1, y1 = src
            x2, y2 = dst
            dx = x2-x1   # x offset
            dy = y2-y1   # y offset
            d = numpy.sqrt(float(dx**2 + dy**2))  # length of edge
            lengths.append(d)

            '''
            Nassim's notes:
            The arrow shape needs to conform to the length of the edge to some degree.
            If the edge is long, the arrow will be very long too, and that can look bad.
            '''
            p = 1.0 - 0.25 / (2*d/100.0)
                
            if d == 0:   # source and target at same position
                continue
            if dx == 0:  # vertical edge
                xa = x2
                ya = dy*p+y1
            if dy == 0:  # horizontal edge
                ya = y2
                xa = dx*p+x1
            else:
                theta = numpy.arctan2(dy, dx)
                thetas.append(theta)
                xa = p*d*numpy.cos(theta)+x1
                ya = p*d*numpy.sin(theta)+y1

                '''
                Nassim's notes:
                You may have noticed that I introduced a new "arrowheads" parameter to the function.
                Since rectangular arrowheads have their place in network modeling (e.g. showing inhibiton),
                I thought that it would be wise to keep the rectangular functionality.
                In this version, we're aiming to make the rectangle thinner, to match notation of inhibition.
                '''
                if arrowheads == False:
                    xa = p*p*d*numpy.cos(theta)+x1
                    ya = p*p*d*numpy.sin(theta)+y1

                    x2 = 1.05*p*p*d*numpy.cos(theta)+x1
                    y2 = 1.05*p*p*d*numpy.sin(theta)+y1


            a_pos.append(((xa, ya), (x2, y2)))

            '''
            Nassim's notes:
            Here is where we calculate the slope of the orthogonal line to the edge.
            Technically, we don't need to re-calculate dx and dy. This can be cleaned up.
            dy DOES have to be checked for its value, however, since we don't want to
            divide by zero.
            '''
            dx2 = x2 - xa
            dy2 = y2 - ya
            if dy2 == 0:
                dy2 = 0.00000000000001

            orthoslope.append((-1.0 * dx2) / dy2)



        if arrowheads:



            '''
            Nassim's notes:
            In order to draw the triangles, we have to give matplotlib three vertices.
            One of the vertices is trivial - it's the endpoint of the edge, or something
            similar along the edge.

            For the other two, we need to solve a system of two equations:
            The distance formula, and the line equation for the orthogonal line.
            The mess down here are the results of that calculation.
            '''
            

            '''
            Nassim's notes:
            The multiplier 2 here helps control the width of the arrows.
            This can be played around with, or even made into a function input if necessary.
            '''
            dist = [2. * ww for ww in lw]

            
            vertex1_x = []
            vertex1_y = []
            vertex2_x = []
            vertex2_y = []

            for i in range(0,len(a_pos)):
                
                if i + 1 > len(dist):
                    dist_to_use =  p * dist[i % len(dist)] 
                else:
                    dist_to_use =  p * dist[i]

                if (((dist_to_use)**2)/(1 + orthoslope[i])) < 0:
                    arrow_width = 0.5 * numpy.sqrt(-1*(dist_to_use)**2/(1 + orthoslope[i]))
                else:
                    arrow_width = numpy.sqrt((dist_to_use)**2/(1 + orthoslope[i]))

                vertex1_x.append(a_pos[i][0][0] + arrow_width)
                vertex2_x.append(a_pos[i][0][0] - arrow_width)
                
                '''
                Nassim's notes:
                This code works just as well if you use the same x vertex for both y values
                and just flip the sign of the orthoslope term. 
                This current implementation was chosen because it makes more mathematical sense.
                '''
                vertex1_y.append(a_pos[i][0][1] + 1.0*orthoslope[i]*(vertex1_x[i] - a_pos[i][0][0]))
                vertex2_y.append(a_pos[i][0][1] + 1.0*orthoslope[i]*(vertex2_x[i] - a_pos[i][0][0]))
                

            '''
            Nassim's notes:
            Here is where we put together our vertices in a matplotlib-readable format.
            The apos_on_edge*lengths[i] multiplier here is tuneable.
            This controls where along the edge the arrow will appear.
            '''

            a_verts = [((vertex1_x[i] - apos_on_edge*lengths[i]*numpy.cos(thetas[i]),vertex1_y[i] - apos_on_edge*lengths[i]*numpy.sin(thetas[i])),
                        (vertex2_x[i] - apos_on_edge*lengths[i]*numpy.cos(thetas[i]),vertex2_y[i] - apos_on_edge*lengths[i]*numpy.sin(thetas[i])),
                        (a_pos[i][1][0] - apos_on_edge*lengths[i]*numpy.cos(thetas[i]),a_pos[i][1][1] - apos_on_edge*lengths[i]*numpy.sin(thetas[i])))
                       for i in range(0,len(a_pos))]

            '''
            Nassim's notes:
            For triangles, you can specify different colors for the face of the triangle and the edges.
            I selected brown here so that the arrows would have a bit of an outline.
            Again, this could be made into a function input.
            '''
            arrow_collection = matplotlib.collections.PolyCollection(a_verts,edgecolors = 'brown',
                                                                     facecolors = arrow_colors,
                                                                     antialiaseds = (1,),
                                                                     transOffset = ax.transData,
                                                                     )

        else:
            '''
            Nassim's notes:
            This is the procedure from the original version of this function.
            I increased the linewidth multiplier, but other than that it's the same.
            '''
            arrow_collection = LineCollection(a_pos,
                        colors=arrow_colors,
                        linewidths=[10.*ww for ww in lw],
                        antialiaseds=(1,),
                        transOffset = ax.transData,
                        )

        
        arrow_collection.set_zorder(1)  # edges go behind nodes
        arrow_collection.set_label(label)
        ax.add_collection(arrow_collection)

    # update view
    minx = numpy.amin(numpy.ravel(edge_pos[:, :, 0]))
    maxx = numpy.amax(numpy.ravel(edge_pos[:, :, 0]))
    miny = numpy.amin(numpy.ravel(edge_pos[:, :, 1]))
    maxy = numpy.amax(numpy.ravel(edge_pos[:, :, 1]))

    w = maxx-minx
    h = maxy-miny
    padx,  pady = 0.05*w, 0.05*h
    corners = (minx-padx, miny-pady), (maxx+padx, maxy+pady)
    ax.update_datalim(corners)
    ax.autoscale_view()


    return edge_collection
