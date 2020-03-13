def backhaul_distance(nodes, country, path_regions):
    """
    """
    country_id = country['country']
    level = country['regional_level']

    filename = 'regions_{}_{}.shp'.format(level, country_id)
    folder = os.path.join(DATA_INTERMEDIATE, country_id, 'regions_lowest')
    path = os.path.join(folder, filename)

    region_data = gpd.read_file(path)
    regions = region_data.to_dict('records')

    idx = index.Index()

    fibre_points_with_id = []
    point_id = 0
    for node in nodes:
        fibre_point = {
            'type': 'Polygon',
            'geometry': node['geometry'],
            'properties': {
                'point_id': point_id,
            }
        }
        fibre_points_with_id.append(fibre_point)
        idx.insert(
            point_id,
            shape(node['geometry']).bounds,
            fibre_point)
        point_id += 1

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")

    output_csv = []
    output_shape = []

    for region in regions:

        geom = shape(region['geometry']).representative_point()

        nearest = [i for i in idx.nearest((geom.bounds))][0]
        region['point_id'] = nearest

        for fibre_point in fibre_points_with_id:
            if nearest == fibre_point['properties']['point_id']:

                geom1 = shape(fibre_point['geometry'])

                x1 = list(geom1.coords)[0][0]
                y1 = list(geom1.coords)[0][1]

                x1, y1 = transformer.transform(x1, y1)

        geom2 = unary_union(region['geometry']).representative_point()

        x2 = list(geom2.coords)[0][0]
        y2 = list(geom2.coords)[0][1]

        x2, y2 = transformer.transform(x2, y2)

        line = LineString([
            (x1, y1),
            (x2, y2)
        ])

        output_csv.append({
            'GID_{}'.format(level): region['GID_{}'.format(level)],
            'distance_km': line.length,
        })

        output_shape.append({
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': (
                    (list(geom1.coords)[0][0], list(geom1.coords)[0][1]),
                    (list(geom2.coords)[0][0], list(geom2.coords)[0][1])
                )
            },
            'properties': {
                'region': region['GID_{}'.format(level)],
            }
        })

    output_csv = pd.DataFrame(output_csv)

    return output_csv, output_shape
