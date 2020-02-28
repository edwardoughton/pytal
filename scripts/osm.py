"""
This contains functions adapted from the code repo for Koks et al. 2019.


"""

def planet_osm():
    """
    This function will download the planet file from the OSM servers.

    """
    osm_path_in = os.path.join(DATA_RAW,'planet_osm')

    # create directory to save planet osm file if that directory does not exit yet.
    if not os.path.exists(osm_path_in):
        os.makedirs(osm_path_in)

    # if planet file is not downloaded yet, download it.
    if 'planet-latest.osm.pbf' not in os.listdir(osm_path_in):

        url = 'https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf'
        urllib.request.urlretrieve(url, os.path.join(osm_path_in,'planet-latest.osm.pbf'))

    else:
        print('Planet file is already downloaded')


def poly_files(data_path, global_shape, save_shapefile=False, regionalized=False):

    """
    This function will create the .poly files from the world shapefile. These
    .poly files are used to extract data from the openstreetmap files.

    This function is adapted from the OSMPoly function in QGIS.

    Arguments:
        *data_path* : base path to location of all files.

        *global_shape*: exact path to the global shapefile used to create the poly files.

    Optional Arguments:
        *save_shape_file* : Default is **False**. Set to **True** will the new shapefile
        with the countries that we include in this analysis will be saved.

        *regionalized*  : Default is **False**. Set to **True** will perform the analysis
        on a regional level.

    Returns:
        *.poly file* for each country in a new dir in the working directory.
    """
# =============================================================================
#     """ Create output dir for .poly files if it is doesnt exist yet"""
# =============================================================================
    poly_dir = os.path.join(data_path,'country_poly_files')

    if regionalized == True:
        poly_dir = os.path.join(data_path,'regional_poly_files')

    if not os.path.exists(poly_dir):
        os.makedirs(poly_dir)

# =============================================================================
#     """ Set the paths for the files we are going to use """
# =============================================================================
    wb_poly_out = os.path.join(data_path,'input_data','country_shapes.shp')

    if regionalized == True:
        wb_poly_out = os.path.join(data_path,'input_data','regional_shapes.shp')

# =============================================================================
#   """Load country shapes and country list and only keep the required countries"""
# =============================================================================
    wb_poly = geopandas.read_file(global_shape)

    # filter polygon file
    if regionalized == True:
        wb_poly = wb_poly.loc[wb_poly['GID_0'] != '-']
        wb_poly = wb_poly.loc[wb_poly['TYPE_1'] != 'Water body']

    else:
        # print(wb_poly)
        wb_poly = wb_poly.loc[wb_poly['GID_0'] != '-']
        # wb_poly = wb_poly.loc[wb_poly['ISO_3digit'] != '-']

    wb_poly.crs = {'init' :'epsg:4326'}

    # and save the new country shapefile if requested
    if save_shapefile == True:
        wb_poly.to_file(wb_poly_out)

    # we need to simplify the country shapes a bit. If the polygon is too diffcult,
    # osmconvert cannot handle it.
#    wb_poly['geometry'] = wb_poly.simplify(tolerance = 0.1, preserve_topology=False)

# =============================================================================
#   """ The important part of this function: create .poly files to clip the country
#   data from the openstreetmap file """
# =============================================================================
    num = 0
    # iterate over the counties (rows) in the world shapefile
    for f in wb_poly.iterrows():
        f = f[1]
        num = num + 1
        geom=f.geometry

#        try:
        # this will create a list of the different subpolygons
        if geom.geom_type == 'MultiPolygon':
            polygons = geom

        # the list will be lenght 1 if it is just one polygon
        elif geom.geom_type == 'Polygon':
            polygons = [geom]

        # define the name of the output file, based on the ISO3 code
        ctry = f['GID_0']
        if regionalized == True:
            attr=f['GID_1']
        else:
            attr=f['GID_0']

        # start writing the .poly file
        f = open(poly_dir + "/" + attr +'.poly', 'w')
        f.write(attr + "\n")

        i = 0

        # loop over the different polygons, get their exterior and write the
        # coordinates of the ring to the .poly file
        for polygon in polygons:

            if ctry == 'CAN':

                x = polygon.centroid.x
                if x < -90:
                    x = -90
                y = polygon.centroid.y
                dist = distance((x,y), (83.24,-79.80), ellipsoid='WGS-84').kilometers
                if dist < 2000:
                    continue

            if ctry == 'RUS':
                x = polygon.centroid.x
                if x < -90:
                    x = -90
                if x > 90:
                    x = 90
                y = polygon.centroid.y
                dist = distance((x,y), (58.89,82.26), ellipsoid='WGS-84').kilometers
                if dist < 500:
                    continue

            polygon = np.array(polygon.exterior)

            j = 0
            f.write(str(i) + "\n")

            for ring in polygon:
                j = j + 1
                f.write("    " + str(ring[0]) + "     " + str(ring[1]) +"\n")

            i = i + 1
            # close the ring of one subpolygon if done
            f.write("END" +"\n")

        # close the file when done
        f.write("END" +"\n")
        f.close()
#        except:
#            print(f['GID_1'])


def clip_osm(data_path,planet_path,area_poly,area_pbf):
    """
    Clip the an area osm file from the larger continent (or planet) file and
    save to a new osm.pbf file. This is much faster compared to clipping the
    osm.pbf file while extracting through ogr2ogr.

    This function uses the osmconvert tool, which can be found at
    http://wiki.openstreetmap.org/wiki/Osmconvert.

    Either add the directory where this executable is located to your
    environmental variables or just put it in the 'scripts' directory.

    Arguments:
        *continent_osm*: path string to the osm.pbf file of the continent
        associated with the country.

        *area_poly*: path string to the .poly file, made through the
        'create_poly_files' function.

        *area_pbf*: path string indicating the final output dir and output
        name of the new .osm.pbf file.

    Returns:
        a clipped .osm.pbf file.
    """
    import os
    import configparser
    CONFIG = configparser.ConfigParser()
    CONFIG.read(os.path.join('scripts', 'script_config.ini'))
    BASE_PATH = CONFIG['file_locations']['base_path']

    print('{} started!'.format(area_pbf))
    # osm_convert_path = 'D:\github\pytal\data\osmconvert64\osmconvert64-0.8.8p'
    osm_convert_path = os.path.join(BASE_PATH,'osmconvert64','osmconvert64-0.8.8p')
    try:
        if (os.path.exists(area_pbf) is not True):
            os.system('{}  {} -B={} -o={}'.format( \
                osm_convert_path,planet_path,area_poly,area_pbf)) # --complete-ways
            print('{} finished!'.format(area_pbf))

    except:
        print('{} did not finish!'.format(area_pbf))

    return print('Complete')


def all_countries(subset = [], regionalized=False, reversed_order=False):
    """
    Clip all countries from the planet osm file and save them to individual osm.pbf files

    Optional Arguments:
        *subset* : allow for a pre-defined subset of countries. REquires ISO3 codes.
        Will run all countries if left empty.

        *regionalized* : Default is **False**. Set to **True** if you want to have the
        regions of a country as well.

        *reversed_order* : Default is **False**. Set to **True**  to work backwards for
        a second process of the same country set to prevent overlapping calculations.

    Returns:
        clipped osm.pbf files for the defined set of countries (either the whole world
        by default or the specified subset)

    """

    # set data path
    data_path = DATA_INTERMEDIATE

    # path to planet file
    planet_path = os.path.join(DATA_RAW,'planet_osm','planet-latest.osm.pbf')

    # global shapefile path
    if regionalized == True:
        world_path = os.path.join(data_path,'global_regions.shp')
    else:
        world_path = os.path.join(data_path,'global_countries.shp')

    # create poly files for all countries
    poly_files(data_path,world_path,save_shapefile=False,regionalized=regionalized)

    # prepare lists for multiprocessing
    if not os.path.exists(os.path.join(data_path,'country_poly_files')):
        os.makedirs(os.path.join(data_path,'country_poly_files'))

    if not os.path.exists(os.path.join(data_path,'country_osm')):
        os.makedirs(os.path.join(data_path,'country_osm'))

    if regionalized == False:

        get_poly_files = os.listdir(os.path.join(data_path,'country_poly_files'))
        if len(subset) > 0:
            polyPaths = [os.path.join(data_path,'country_poly_files',x) for x in \
                            get_poly_files if x[:3] in subset]
            area_pbfs = [os.path.join(data_path,'region_osm_admin1', \
                            x.split('.')[0]+'.osm.pbf') for x in \
                            get_poly_files if x[:3] in subset]
        else:
            polyPaths = [os.path.join(data_path,'country_poly_files',x) for x in \
                            get_poly_files]
            area_pbfs = [os.path.join(data_path,'region_osm_admin1', \
                            x.split('.')[0]+'.osm.pbf') for x in get_poly_files]

        big_osm_paths = [planet_path]*len(polyPaths)

    elif regionalized == True:

        if not os.path.exists(os.path.join(data_path,'regional_poly_files')):
            os.makedirs(os.path.join(data_path,'regional_poly_files'))

        if not os.path.exists(os.path.join(data_path,'region_osm')):
            os.makedirs(os.path.join(data_path,'region_osm_admin1'))

        get_poly_files = os.listdir(os.path.join(data_path,'regional_poly_files'))
        if len(subset) > 0:
            polyPaths = [os.path.join(data_path,'regional_poly_files',x) for x in \
                            get_poly_files if x[:3] in subset]
            area_pbfs = [os.path.join(data_path,'region_osm_admin1', \
                            x.split('.')[0]+'.osm.pbf') for x in \
                            get_poly_files if x[:3] in subset]
            big_osm_paths = [os.path.join(DATA_RAW,'planet_osm', \
                                x[:3]+'.osm.pbf') for x in \
                                get_poly_files if x[:3] in subset]
        else:
            polyPaths = [os.path.join(data_path,'regional_poly_files',x) \
                            for x in get_poly_files]
            area_pbfs = [os.path.join(data_path,'region_osm_admin1', \
                            x.split('.')[0]+'.osm.pbf') for x in get_poly_files]
            big_osm_paths = [os.path.join(DATA_RAW,'planet_osm', \
                                x[:3]+'.osm.pbf') for x in get_poly_files]

    data_paths = [data_path]*len(polyPaths)

    # allow for reversed order if you want to run two at the same time
    # (convenient to work backwards for the second process, to prevent
    # overlapping calculation)
    if reversed_order == True:
        polyPaths = polyPaths[::-1]
        area_pbfs = area_pbfs[::-1]
        big_osm_paths = big_osm_paths[::-1]

    # extract all country osm files through multiprocesing
    pool = Pool(cpu_count()-1)
    pool.starmap(clip_osm, zip(data_paths, big_osm_paths, polyPaths, area_pbfs))


if __name__ == '__main__':

    planet_osm()

    poly_files()

    all_countries(subset = [], regionalized=False, reversed_order=True)
