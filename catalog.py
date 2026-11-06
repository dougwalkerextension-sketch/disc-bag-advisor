"""Small, source-linked starter catalog. Flight numbers are guidance, not guarantees."""
ROWS = [
    ('Discraft','Buzzz',5,4,-1,1,'midrange','https://www.team.discraft.com/discs/buzzz'),
    ('Discmania','FD',7,6,0,1,'fairway','https://www.discmania.net/products/c-line-fd'),
    ('Streamline','Drift',7,5,-2,1,'fairway','https://streamlinediscs.com/discs/drift/'),
    ('Innova','Leopard3',7,5,-2,1,'fairway','https://www.innovadiscs.com/disc/leopard3/'),
    ('Innova','Leopard',6,5,-2,1,'fairway','https://www.innovadiscs.com/disc/leopard/'),
    ('Innova','TeeBird',7,5,0,2,'fairway','https://www.innovadiscs.com/disc/teebird/'),
    ('Innova','Firebird',9,3,0,4,'fairway','https://www.innovadiscs.com/disc/firebird/'),
    ('Innova','Sidewinder',9,5,-3,1,'fairway','https://www.innovadiscs.com/disc/sidewinder/'),
    ('Innova','Mako3',5,5,0,0,'midrange','https://www.innovadiscs.com/disc/mako3/'),
    ('Innova','Roc3',5,4,0,3,'midrange','https://www.innovadiscs.com/disc/roc3/'),
    ('Innova','Aviar',2,3,0,1,'putter','https://www.innovadiscs.com/disc/aviar/'),
    ('Innova','Destroyer',12,5,-1,3,'distance','https://www.innovadiscs.com/disc/destroyer/'),
    ('Latitude 64','River',7,7,-1,1,'fairway','https://latitude64.com/products/opto-river'),
    ('Latitude 64','Diamond',8,6,-3,1,'fairway','https://latitude64.com/products/opto-diamond'),
    ('Latitude 64','Explorer',7,5,0,2,'fairway','https://latitude64.com/products/opto-explorer'),
    ('Latitude 64','Fuse',5,6,-1,0,'midrange','https://latitude64.com/products/opto-fuse'),
    ('Latitude 64','Pure',3,3,-1,1,'putter','https://latitude64.com/products/opto-pure'),
    ('MVP','Relay',6,5,-2,1,'fairway','https://mvpdiscsports.com/discs/relay/'),
    ('MVP','Signal',6,5,-3,1,'fairway','https://mvpdiscsports.com/discs/signal/'),
    ('MVP','Volt',8,5,-0.5,2,'fairway','https://mvpdiscsports.com/discs/volt/'),
    ('MVP','Wave',11,5,-2,2,'distance','https://mvpdiscsports.com/discs/wave/'),
    ('Axiom','Crave',6.5,5,-1,1,'fairway','https://axiomdiscs.com/discs/crave/'),
    ('Axiom','Hex',5,5,-1,1,'midrange','https://axiomdiscs.com/discs/hex/'),
    ('Axiom','Envy',3,3,0,2,'putter','https://axiomdiscs.com/discs/envy/'),
]
CATALOG = [dict(id=f'{r[0]}-{r[1]}'.lower().replace(' ','-'),brand=r[0],name=r[1],
    speed=r[2],glide=r[3],turn=r[4],fade=r[5],category=r[6],source=r[7]) for r in ROWS]

# OTB's reported 2025 retail sales, not a claim about worldwide market share.
POPULAR_BRANDS = ['Discraft','Axiom','MVP','Innova','Discmania']
BRANDS = POPULAR_BRANDS + sorted({d['brand'] for d in CATALOG}-set(POPULAR_BRANDS))
BRAND_POPULARITY_SOURCE = 'https://otbdiscs.com/otbs-top-100-discs-of-2025/'

def get_disc(disc_id):
    return next((dict(d) for d in CATALOG if d['id']==disc_id), None)
