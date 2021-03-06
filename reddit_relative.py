import sys
from pyspark.sql import SparkSession, functions, types

spark = SparkSession.builder.appName('reddit relative scores').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 5) # make sure we have Python 3.5+
assert spark.version >= '2.3' # make sure we have Spark 2.3+

comments_schema = types.StructType([
    types.StructField('archived', types.BooleanType()),
    types.StructField('author', types.StringType()),
    types.StructField('author_flair_css_class', types.StringType()),
    types.StructField('author_flair_text', types.StringType()),
    types.StructField('body', types.StringType()),
    types.StructField('controversiality', types.LongType()),
    types.StructField('created_utc', types.StringType()),
    types.StructField('distinguished', types.StringType()),
    types.StructField('downs', types.LongType()),
    types.StructField('edited', types.StringType()),
    types.StructField('gilded', types.LongType()),
    types.StructField('id', types.StringType()),
    types.StructField('link_id', types.StringType()),
    types.StructField('name', types.StringType()),
    types.StructField('parent_id', types.StringType()),
    types.StructField('retrieved_on', types.LongType()),
    types.StructField('score', types.LongType()),
    types.StructField('score_hidden', types.BooleanType()),
    types.StructField('subreddit', types.StringType()),
    types.StructField('subreddit_id', types.StringType()),
    types.StructField('ups', types.LongType()),
    #types.StructField('year', types.IntegerType()),
    #types.StructField('month', types.IntegerType()),
])


def main(in_directory, out_directory):
    comments = spark.read.json(in_directory, schema=comments_schema)
    comments = comments.select(comments['subreddit'], comments['author'], comments['score']).cache()
   
    avg_scores = comments.groupBy('subreddit').avg('score').withColumnRenamed('avg(score)', 'avg_score')
    avg_scores = avg_scores.filter(avg_scores.avg_score >= 0)
  
    join_avg_score = comments.join(avg_scores, on ='subreddit')

    
    rel_score = join_avg_score.withColumn('rel_score', join_avg_score.score/join_avg_score.avg_score ).cache()

    max_rel_score = rel_score.groupBy('subreddit').max('rel_score').withColumnRenamed('max(rel_score)', 'max_rel_score')

 #.hint('broadcast')

    filtered_scores= joined_max.filter(joined_max.rel_score == joined_max.max_rel_score).sort('subreddit')

    best_comments = filtered_scores.select(filtered_scores['subreddit'], filtered_scores['author'], filtered_scores['rel_score']).sort('rel_score')
    best_comments.show()



    best_comments.write.json(out_directory, mode='overwrite')



if __name__=='__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)
