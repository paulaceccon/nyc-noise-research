/* global geojson, leafletPip, L */

function pointInPolygon(points, dict)
{
    if (geojson === undefined)
        return;
    
    var pip = {};
    
    var point;
    var desc;
    var result;
    var obj;
    
    for (var i = 0; i < points.length; i++)
    {
        point = points[i].slice(0,2);
        desc  = points[i].slice(2);

        result = leafletPip.pointInLayer(point, geojson, true);
        
        if (result.length === 0)
            continue;
        
        if (!pip.hasOwnProperty(result[0].feature.id))
        {   
            obj = {};
            for (var key in dict)
                obj[key] = 0;
            pip[result[0].feature.id] = obj;
        }
        
        pip[result[0].feature.id][desc] += 1;
    }   
//    console.log(pip);
    return pip;
}