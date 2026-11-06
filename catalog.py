"""Small, source-linked starter catalog. Flight numbers are guidance, not guarantees."""
ROWS = [
    ('Kastaplast', 'Falk', 9, 6, -2, 1, 'fairway', 'https://www.kastaplast.com/products/k1-falk'),
    ('RPM', 'Piwakawaka', 6, 6, -3, 0, 'midrange', 'https://www.rpmdiscs.com/product/piwakawaka/'),
    ('Dynamic Discs', 'Escape', 9, 5, -1, 2, 'fairway', 'https://www.dynamicdiscs.com/products/lucid-escape'),
    ('Westside', 'Underworld', 7, 6, -3, 1, 'fairway', 'https://westsidediscs.com/products/vip-underworld'),
    ('Clash Discs', 'Soda', 7, 5, -2, 2, 'fairway', 'https://www.clashdiscs.com/steady-soda'),
    ('Thought Space Athletics', 'Pathfinder', 5, 5, 0, 1, 'midrange', 'https://thoughtspaceathletics.com/collections/pathfinder'),
    ('Infinite Discs', 'Sphinx', 9, 6, -3, 1, 'fairway', 'https://infinitediscs.com/infinite-discs-sphinx'),
    ('Mint Discs', 'Jackalope', 8, 5, -2, 1, 'fairway', 'https://mintdiscs.com/products/jackalope-apex-plastic-ap-jl01-22'),
    ('Prodigy', 'F5', 8, 6, -2, 1, 'fairway', 'https://prodigydisc.com/products/prodigy-f5-400-plastic'),
    ('Divergent Discs', 'Kraken', 8, 5, -1, 2, 'fairway', 'https://divergentdiscs.com/product-tag/kraken/'),
    ('Doomsday Discs', 'Blackout', 8, 5, -2, 1, 'fairway', 'https://doomsdaydiscs.com/products/blackout-in-toxic-waste-plastic'),
    ('Gateway', 'Wizard', 2, 3, 0, 2, 'putter', 'https://gatewaydiscsports.com/products/wizard-ss'),
    ('Elevation', 'Koi', 3, 4, -2, 0, 'putter', 'https://www.elevationdiscs.com/product-page/koi-glo-g'),

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

# Explicit coverage snapshot: every manufacturer on the user-supplied DiscList page.
# Rankings are an attributed snapshot, not live sales or a complete world directory.
MANUFACTURERS = ['Innova','Axiom','Discraft','Discmania','MVP','Latitude 64',
    'Kastaplast','RPM','Dynamic Discs','Westside','Clash Discs','Streamline',
    'Thought Space Athletics','Infinite Discs','Mint Discs','Prodigy',
    'Divergent Discs','Doomsday Discs','Gateway','Elevation']
POPULAR_BRANDS = MANUFACTURERS[:5]
BRANDS = POPULAR_BRANDS + sorted(set(MANUFACTURERS)-set(POPULAR_BRANDS))
BRAND_POPULARITY_SOURCE = 'https://thedisclist.com/brands/'
BRAND_RANKING_DATE = '2026-10-16'


def get_disc(disc_id):
    return next((dict(d) for d in CATALOG if d['id']==disc_id), None)
