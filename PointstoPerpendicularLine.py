# -*- coding: utf-8 -*-


from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsVectorLayer,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterNumber
                       )
from qgis import processing


class PPLProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT' # Input line layer
    POINTDISTANCE = 'POINTDISTANCE' # Point distance along geometry
    WIDTH = 'WIDTH' # Line width
    OUTPUT1 = 'OUTPUT1' # Point feature temporary output
    OUTPUT2 = 'OUTPUT2' # Line feature temporary output
    

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PPLProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'myscript'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Points to Perpendicular Lines')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('User Scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("This algortihm allows you to create perpendicular line for a specific distance in line feature")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have line feature.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.POINTDISTANCE,
                self.tr('Point Distance Along Line')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.WIDTH,
                self.tr('Line Width')
            )
        )
        

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT1,
                self.tr('Output point layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT2,
                self.tr('Output line layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        pointDistance = parameters['POINTDISTANCE']
        
        pointOutputLayer = self.parameterAsVectorLayer(parameters,self.OUTPUT1,context)
        
        pointOutputLayer = processing.run("native:pointsalonglines",
                                            {
                                            'DISTANCE':pointDistance,
                                            'END_OFFSET': 0,
                                            'START_OFFSET': 0,
                                            'INPUT': parameters['INPUT'],
                                            'OUTPUT': parameters['OUTPUT1']
                                            },
                                            context=context,
                                            feedback=feedback,
                                            is_child_algorithm=True
                                            )

        
        outputVectorLayer = self.parameterAsVectorLayer(parameters,self.OUTPUT2,context)
        
        leftRigthWidth = parameters['WIDTH']
        
        geoExpression = 'extend(make_line($geometry,project ($geometry,'+ str(leftRigthWidth) + ',radians("angle" -90))),' + str(leftRigthWidth) + ',0)'
        
        outputVectorLayer = processing.run("native:geometrybyexpression",
                                            {
                                            'EXPRESSION':geoExpression,
                                            'INPUT': pointOutputLayer['OUTPUT'],
                                            'OUTPUT_GEOMETRY': 1,  # Line
                                            'WITH_M': False,
                                            'WITH_Z': False,
                                            'OUTPUT': parameters['OUTPUT2']
                                            }
                                            ,context=context,
                                            feedback=feedback,
                                            is_child_algorithm=True)
        
        

        # Return the results of the algorithm. In this case our only result is
        # the line feature which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        
        return {'OUTPUT1': pointOutputLayer['OUTPUT'],'OUTPUT2': outputVectorLayer['OUTPUT']}
