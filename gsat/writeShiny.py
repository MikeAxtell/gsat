import re
import os.path

def writeShiny (sqliteFile, odir, mfile):
    appFile = re.sub('.sqlite$', '.app.R', sqliteFile) 
    sqliteBase = re.sub('^.*\/', '', sqliteFile)
    appBase = re.sub('^.*\/', '', appFile)
    fh = open(appFile, "wt")
    fh.write("library(shiny)\n")
    fh.write("library(ggplot2)\n")
    fh.write("library(DBI)\n")
    fh.write("library(DT)\n")
    fh.write('mydb <- dbConnect(RSQLite::SQLite(), "')
    fh.write(sqliteBase)
    fh.write('")')
    fh.write("\n")
    # file tests for mfile and for triminfo.csv
    triminfoFile = odir.rstrip("/") + '/triminfo.csv'

    appCode_c1 = getAppCode_c1()
    fh.write(appCode_c1)

    if os.path.isfile(triminfoFile):
        appCode_trim = getAppCode_trim()
        fh.write(appCode_trim)
        
    if os.path.isfile(mfile):
        appCode_mat = getAppCode_mat()
        fh.write(appCode_mat)

    fh.write('ui <- navbarPage("gsat",')
    fh.write("\n")

    if os.path.isfile(triminfoFile):
        tabPanel_trim = get_tabPanel_trim()
        fh.write(tabPanel_trim)

    tabPanel_lib = get_tabPanel_lib()
    fh.write(tabPanel_lib)

    
    if os.path.isfile(mfile):
        tabPanel_mat = get_tabPanel_mat()
        fh.write(tabPanel_mat)

    appCode_c2 = get_appCode_c2()
    fh.write(appCode_c2)
    fh.close()

    return appBase

def get_appCode_c2():
    appCode_c2 = """
position='fixed-top',
               tags$style(type="text/css", "body {padding-top: 70px;}")

)

# Define server logic required to draw plots
server <- function(input, output) {
    
    output$variants <- DT::renderDataTable(
        dbGetQuery(mydb, paste(
            "SELECT sequence, length(sequence) AS 'length', editDistance, SUM(raw) as 'raw' FROM mature",
            " WHERE matureName = '", qsrnas$matureName[input$qsrnaTable_rows_selected],
            "' GROUP BY sequence ORDER BY SUM(raw) DESC", sep=""
        ))
    )
    
    output$matPlot <- renderPlot({
        # build the db query, for clarity
        mPq <- paste("SELECT mature.sample, SUM(",
                     input$qPlotUnit,
                     ") AS ", input$qPlotUnit,
                     ", metadata.", input$factor1, 
                     ", metadata.", input$factor2,
                     " FROM mature JOIN metadata ON ",
                     "metadata.sample = mature.sample",
                     " WHERE matureName = '", qsrnas$matureName[input$qsrnaTable_rows_selected],
                     "' AND editDistance <= ", input$eds_choice,
                     " GROUP BY mature.sample",
                     sep=""
                     )
        # Get the data.frame
        mPd <- dbGetQuery(mydb, mPq)
        # Plot it
        ggplot(data = mPd,
               aes_string(x=colnames(mPd)[3], 
                          y=colnames(mPd)[2], 
                          color=colnames(mPd)[4])) +
            geom_jitter(position = position_jitterdodge(),
                        size=4, shape=1, stroke=1.5) +
            scale_y_continuous(limits = c(0, NA)) +
            ggtitle(paste(qsrnas$matureName[input$qsrnaTable_rows_selected],
                          "by", colnames(mPd)[3], "and",
                          colnames(mPd)[4], "in units of",
                          colnames(mPd)[2]
                          ))
        
        
    })
    
    output$qsrnaTable <- DT::renderDataTable(
        qsrnas, selection=list(mode='single', target='row', selected=1),
        rownames=FALSE,
        options = list(lengthMenu = list(c(5,30,-1), c("5","30","All")),
                       pageLength = 5)
    )
    
    output$mdtable <- renderDataTable(
        md, selection=list(mode='single', target='row',selected=1),
        rownames=FALSE,
        options = list(lengthMenu = list(c(5, 30, -1), c("5","30","All")),
                       pageLength = 5)
    )
    output$trimBar <- renderPlot({
        if(input$plotType == "count") {
            ggplot(data = td,
                aes(x=sample, y=count, fill=category)) +
            geom_bar(stat="identity") +
            ggtitle("Trim Information - Counts") +
            theme(axis.text.x = element_text(angle = 90, hjust = 1))
        } else if (input$plotType == "proportion") {
            ggplot(data = td,
                 aes(x=sample, y=proportion, fill=category)) +
            geom_bar(stat="identity") +
            ggtitle("Trim Information - Proportion") +
            theme(axis.text.x = element_text(angle = 90, hjust = 1))
        }
    })
    
    output$trimTable <- renderDataTable(
        td, rownames=FALSE,
        options=list(lengthMenu=list(c(10,50,-1),c("10","50","All"))),
        selection='none'
    )
    
    output$libBarPlot <- renderPlot({
        lbp <- dbGetQuery(mydb, 
                   paste("SELECT size, firstBase, count FROM libinfo 
                         WHERE sample = '", 
                         md$sample[input$mdtable_rows_selected[1]], "' AND countType = '", 
                         input$libPlotType, "' ORDER BY size, firstBase", sep=''))
        ggplot(data = lbp,
              aes(x=size, y=count, fill=firstBase)) +
            geom_bar(stat="identity") +
            ggtitle(paste(md$sample[input$mdtable_rows_selected[1]],
                          "details by", input$libPlotType)) +
            coord_cartesian(xlim=input$libSize, ylim=c(0,input$libPlotMax))
    })
    
    output$libMetaData <- renderTable (
        dbGetQuery(mydb, paste("SELECT * FROM metadata WHERE sample ='",
                               input$libsample, "'", sep=''))
    )
    
    output$libProfiles <- renderPlot({

        lp_sample = md$sample[input$mdtable_rows_selected[1]]

        lp_this <- lp_all[lp_all$sample == lp_sample &
                              lp_all$countType == input$libPlotType, ]
        lp_others <- lp_all[lp_all$sample != lp_sample &
                                lp_all$countType == input$libPlotType, ]
        ggplot(data = lp_others,
               aes(x=size, y=count, group=sample)) +
            geom_line(aes(color="otherSamples")) + geom_point(color="gray") +
            geom_line(data=lp_this, aes(color="selectedSample")) +
            geom_point(data=lp_this, color="red") +
            ggtitle(paste(lp_sample,
                    "vs. all other samples by", input$libPlotType)) +
            scale_color_manual(name="sample", values=c(
                otherSamples="gray",selectedSample="red"
            )) +
            coord_cartesian(xlim=input$libSize, ylim=c(0,input$libPlotMax))
        
    })
    
}
    


# Point your browser to the url shown below. Use ctl-c to quit.
shinyApp(ui = ui, server = server)



"""
    return appCode_c2

def get_tabPanel_mat():
    tabPanel_mat = """
tabPanel("Queried sRNAs",
                            sidebarLayout(
                                sidebarPanel(width = 5,
                                             h3("Select a sequence"),
                                             div(DT::dataTableOutput('qsrnaTable'),
                                                 style = "font-size: 80%; width: 80%"),
                                             h3("Plot Controls"),
                                             fluidRow(
                                                 column(6, 
                                                        radioButtons("qPlotUnit", "Unit of measure",
                                                                     choices = c("raw","rpm"),
                                                                     selected = "rpm")
                                                 ),
                                                 column(6,
                                                        radioButtons("eds_choice",
                                                                     "Max Edit Distance",
                                                                     choices = eds$editDistance,
                                                                     selected = max(eds$editDistance)
                                                        )
                                                 )
                                             ),
                                             fluidRow(
                                                 column(6,
                                                        radioButtons("factor1","Factor 1",
                                                                     choices=colnames(md)[2:length(colnames(md))]
                                                        )),
                                                 column(6,
                                                        radioButtons("factor2","Factor 2",
                                                                     choices=colnames(md)[2:length(colnames(md))],
                                                                     selected=colnames(md)[length(colnames(md))]
                                                        ))
                                             )
                                ),
                                mainPanel(width = 7,
                                          h3("sRNA Accumulation"),
                                          plotOutput('matPlot'),
                                          h3("sRNA Variants"),
                                          DT::dataTableOutput('variants')
                                )
                            )
                            
                   ),
"""
    return tabPanel_mat

def get_tabPanel_lib():
    tabPanel_lib = """
tabPanel("Library Info",
                        sidebarLayout(
                            sidebarPanel(width = 5,
                                        h3("Select a library"),
                                        dataTableOutput('mdtable',
                                                        width="75%",
                                                        height="50%"),
                                        h3("Plot controls"),
                                        radioButtons("libPlotType", h4("Plot Type"),
                                                    choices = c("abun","unique")),
                                        sliderInput('libSize', "RNA sizes",
                                                    min = minSize, max = maxSize,
                                                    value=c(minSize, maxSize),
                                                    step=1),
                                        sliderInput('libPlotMax', "Maximum count",
                                                    min = 0, max = (1.1 * maxCount),
                                                    value=(1.1*maxCount))),
                            mainPanel(width = 7,
                                      h3("Library profile"),
                                      plotOutput('libProfiles'),
                                      plotOutput('libBarPlot'))
                        )
               ),
"""
    return tabPanel_lib

def get_tabPanel_trim ():
    tabPanel_trim = """
tabPanel("Trim Info",
                        radioButtons("plotType", h4("Plot Type"),
                                choices = c("count", "proportion"),
                                selected = "count"),
                        plotOutput("trimBar"),
                        dataTableOutput('trimTable')
                    ),

"""
    return tabPanel_trim

def getAppCode_mat ():
    appCode_mat = """
ex_mature = dbExistsTable(mydb, "mature")
if(ex_mature == TRUE) {
    qsrnas <- dbGetQuery(mydb, paste(
        "SELECT matureName, SUM(raw) as 'totalRaw'",
        "FROM mature GROUP BY matureName ORDER BY matureName"))

    # Determine the range of possible edit distances
    eds <- dbGetQuery(mydb, "SELECT DISTINCT editDistance FROM mature")
}

"""
    return appCode_mat

def getAppCode_trim (): 
    appCode_trim = """
ex_trim <- dbExistsTable(mydb, "triminfo")
if(ex_trim == TRUE) {

    td <- dbGetQuery(mydb, "SELECT * FROM triminfo JOIN metadata ON 
                 metadata.sample = triminfo.sample")
    # Delete the duplicate 'sample' column
    td[,4] <- NULL

    # Calculate proportions by sample
    x = vector()
    for (i in 1:nrow(td)) {
        x[i] = sum(td[td$sample == td[i,"sample"], "count"])
    }
    td$proportion = round(td$count / x, 3)
}

"""
    return appCode_trim


def getAppCode_c1 ():
    appCode_c1 = """
    ############ libinfo
# Get list of possible samples
psam <- dbGetQuery(mydb, "SELECT DISTINCT sample FROM libinfo")
# overall size profiles
lp_all <- dbGetQuery(mydb, paste(
    "SELECT sample, size, countType, SUM(count) as 'count' FROM libinfo ",
    "GROUP BY sample, size, countType",
    sep=''))

## Metadata
md <- dbGetQuery(mydb, "SELECT * FROM metadata ORDER BY sample")

## Define slider ranges / boundaries for lib plots

maxCount <- max(lp_all$count)
minSize <- min(lp_all$size)
maxSize <- max(lp_all$size)

"""
    return appCode_c1





def getAppCode ():
    appCode = """
######## get and process triminfo
td <- dbGetQuery(mydb, "SELECT * FROM triminfo JOIN metadata ON 
                 metadata.sample = triminfo.sample")
# Delete the duplicate 'sample' column
td[,4] <- NULL

# Calculate proportions by sample
x = vector()
for (i in 1:nrow(td)) {
    x[i] = sum(td[td$sample == td[i,"sample"], "count"])
}
td$proportion = round(td$count / x, 3)

############ libinfo
# Get list of possible samples
psam <- dbGetQuery(mydb, "SELECT DISTINCT sample FROM libinfo")
# overall size profiles
lp_all <- dbGetQuery(mydb, paste(
    "SELECT sample, size, countType, SUM(count) as 'count' FROM libinfo ",
    "GROUP BY sample, size, countType",
    sep=''))

## Metadata
md <- dbGetQuery(mydb, "SELECT * FROM metadata ORDER BY sample")

## Define slider ranges / boundaries for lib plots

maxCount <- max(lp_all$count)
minSize <- min(lp_all$size)
maxSize <- max(lp_all$size)

## Get a table of all user queries
qsrnas <- dbGetQuery(mydb, paste(
    "SELECT matureName, SUM(raw) as 'totalRaw'",
    "FROM mature GROUP BY matureName ORDER BY matureName"))

# Determine the range of possible edit distances
eds <- dbGetQuery(mydb, "SELECT DISTINCT editDistance FROM mature")


# Define UI for application that draws a histogram
ui <- navbarPage("gsat",
                 tabPanel("Trim Info",
                    radioButtons("plotType", h4("Plot Type"),
                                choices = c("count", "proportion"),
                                selected = "count"),
                    plotOutput("trimBar"),
                    dataTableOutput('trimTable')
                    ),
               tabPanel("Library Info",
                        sidebarLayout(
                            sidebarPanel(width = 5,
                                        h3("Select a library"),
                                        dataTableOutput('mdtable',
                                                        width="75%",
                                                        height="50%"),
                                        h3("Plot controls"),
                                        radioButtons("libPlotType", h4("Plot Type"),
                                                    choices = c("abun","unique")),
                                        sliderInput('libSize', "RNA sizes",
                                                    min = minSize, max = maxSize,
                                                    value=c(minSize, maxSize),
                                                    step=1),
                                        sliderInput('libPlotMax', "Maximum count",
                                                    min = 0, max = (1.1 * maxCount),
                                                    value=(1.1*maxCount))),
                            mainPanel(width = 7,
                                      h3("Library profile"),
                                      plotOutput('libProfiles'),
                                      plotOutput('libBarPlot'))
                        )
               ),
               tabPanel("Queried sRNAs",
                        sidebarLayout(
                            sidebarPanel(width = 5,
                                         h3("Select a sequence"),
                                         div(DT::dataTableOutput('qsrnaTable'),
                                             style = "font-size: 80%; width: 80%"),
                                         h3("Plot Controls"),
                                         fluidRow(
                                             column(6, 
                                                radioButtons("qPlotUnit", "Unit of measure",
                                                    choices = c("raw","rpm"),
                                                    selected = "rpm")
                                                    ),
                                             column(6,
                                                    radioButtons("eds_choice",
                                                        "Max Edit Distance",
                                                        choices = eds$editDistance,
                                                        selected = max(eds$editDistance)
                                                    )
                                             )
                                          ),
                                         fluidRow(
                                             column(6,
                                                    radioButtons("factor1","Factor 1",
                                                      choices=colnames(md)[2:length(colnames(md))]
                                                      )),
                                             column(6,
                                                    radioButtons("factor2","Factor 2",
                                                                 choices=colnames(md)[2:length(colnames(md))],
                                                                 selected=colnames(md)[length(colnames(md))]
                                                    ))
                                         )
                                        ),
                            mainPanel(width = 7,
                                      h3("sRNA Accumulation"),
                                      plotOutput('matPlot'),
                                      h3("sRNA Variants"),
                                      DT::dataTableOutput('variants')
                                      )
                        )
                        
                ),
               position='fixed-top',
               tags$style(type="text/css", "body {padding-top: 70px;}")

)



# Define server logic required to draw plots
server <- function(input, output) {
    
    output$variants <- DT::renderDataTable(
        dbGetQuery(mydb, paste(
            "SELECT sequence, length(sequence) AS 'length', editDistance, SUM(raw) as 'raw' FROM mature",
            " WHERE matureName = '", qsrnas$matureName[input$qsrnaTable_rows_selected],
            "' GROUP BY sequence ORDER BY SUM(raw) DESC", sep=""
        ))
    )
    
    output$matPlot <- renderPlot({
        # build the db query, for clarity
        mPq <- paste("SELECT mature.sample, SUM(",
                     input$qPlotUnit,
                     ") AS ", input$qPlotUnit,
                     ", metadata.", input$factor1, 
                     ", metadata.", input$factor2,
                     " FROM mature JOIN metadata ON ",
                     "metadata.sample = mature.sample",
                     " WHERE matureName = '", qsrnas$matureName[input$qsrnaTable_rows_selected],
                     "' AND editDistance <= ", input$eds_choice,
                     " GROUP BY mature.sample",
                     sep=""
                     )
        # Get the data.frame
        mPd <- dbGetQuery(mydb, mPq)
        # Plot it
        ggplot(data = mPd,
               aes_string(x=colnames(mPd)[3], 
                          y=colnames(mPd)[2], 
                          color=colnames(mPd)[4])) +
            geom_jitter(position = position_jitterdodge(),
                        size=4, shape=1, stroke=1.5) +
            ggtitle(paste(qsrnas$matureName[input$qsrnaTable_rows_selected],
                          "by", colnames(mPd)[3], "and",
                          colnames(mPd)[4], "in units of",
                          colnames(mPd)[2]
                          ))
        
        
    })
    
    output$qsrnaTable <- DT::renderDataTable(
        qsrnas, selection=list(mode='single', target='row', selected=1),
        rownames=FALSE,
        options = list(lengthMenu = list(c(5,30,-1), c("5","30","All")),
                       pageLength = 5)
    )
    
    output$mdtable <- renderDataTable(
        md, selection=list(mode='single', target='row',selected=1),
        rownames=FALSE,
        options = list(lengthMenu = list(c(5, 30, -1), c("5","30","All")),
                       pageLength = 5)
    )
    output$trimBar <- renderPlot({
        if(input$plotType == "count") {
            ggplot(data = td,
                aes(x=sample, y=count, fill=category)) +
            geom_bar(stat="identity") +
            ggtitle("Trim Information - Counts") +
            theme(axis.text.x = element_text(angle = 90, hjust = 1))
        } else if (input$plotType == "proportion") {
            ggplot(data = td,
                 aes(x=sample, y=proportion, fill=category)) +
            geom_bar(stat="identity") +
            ggtitle("Trim Information - Proportion") +
            theme(axis.text.x = element_text(angle = 90, hjust = 1))
        }
    })
    
    output$trimTable <- renderDataTable(
        td, rownames=FALSE,
        options=list(lengthMenu=list(c(10,50,-1),c("10","50","All"))),
        selection='none'
    )
    
    output$libBarPlot <- renderPlot({
        lbp <- dbGetQuery(mydb, 
                   paste("SELECT size, firstBase, count FROM libinfo 
                         WHERE sample = '", 
                         md$sample[input$mdtable_rows_selected[1]], "' AND countType = '", 
                         input$libPlotType, "' ORDER BY size, firstBase", sep=''))
        ggplot(data = lbp,
              aes(x=size, y=count, fill=firstBase)) +
            geom_bar(stat="identity") +
            ggtitle(paste(md$sample[input$mdtable_rows_selected[1]],
                          "details by", input$libPlotType)) +
            coord_cartesian(xlim=input$libSize, ylim=c(0,input$libPlotMax))
    })
    
    output$libMetaData <- renderTable (
        dbGetQuery(mydb, paste("SELECT * FROM metadata WHERE sample ='",
                               input$libsample, "'", sep=''))
    )
    
    output$libProfiles <- renderPlot({

        lp_sample = md$sample[input$mdtable_rows_selected[1]]

        lp_this <- lp_all[lp_all$sample == lp_sample &
                              lp_all$countType == input$libPlotType, ]
        lp_others <- lp_all[lp_all$sample != lp_sample &
                                lp_all$countType == input$libPlotType, ]
        ggplot(data = lp_others,
               aes(x=size, y=count, group=sample)) +
            geom_line(aes(color="otherSamples")) + geom_point(color="gray") +
            geom_line(data=lp_this, aes(color="selectedSample")) +
            geom_point(data=lp_this, color="red") +
            ggtitle(paste(lp_sample,
                    "vs. all other samples by", input$libPlotType)) +
            scale_color_manual(name="sample", values=c(
                otherSamples="gray",selectedSample="red"
            )) +
            coord_cartesian(xlim=input$libSize, ylim=c(0,input$libPlotMax))
        
    })
    
}
    


# Run the application 
shinyApp(ui = ui, server = server)
"""
    return appCode


    
    
